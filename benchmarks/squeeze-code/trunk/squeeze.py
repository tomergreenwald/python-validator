"""Compresses a (set of) file(s) using the best format and the best options."""
# !/usr/bin/python
# -*- coding: utf-8 -*-
# Anthony Labarre © 2013-2014

# TODO cleanup function to remove everything beforehand and afterwards


# TODO additional features:
# * "exhaustive" mode: try all combinations of options for each program
# * file manager extensions (dolphin, thunar, ...)
# * only tested under ubuntu so far, make it cross-platform
# * improve extension: compression(s) can take a long time, so user should see
#   a progress bar to know that something is happening

# TODO add compressors:
# make up my mind about those:
# * mscompress
# * arc
# * dact
# * dar
# * dwz
# * e00compr
# * ewf-tools
# * ha
# * lcab
# * lrzip
# * ncompress
# * nxproxy
# * plzip (to lzip what pbzip2 is to bzip2 ... same problems?)
# * ppmd
# * zp (really different from zpaq?)

# TODO improvements:
# * prefer pbzip2 over bzip2 if both are available; I don't do it yet, because
#   they produce files with different sizes using the same options and I first
#   need to understand why
# * more fine-tuning of misc options for p7zip subprograms
# * for large (define) files, probe size every ... seconds and abort if it
#   exceeds the best size so far -- but then this will mess up percentages...
# * check available free space before compressing
#   -> ok, but how much space left should we demand?
# * squeeze should not stop just because one program failed
#   -> add try / except blocks

# TODO minor issues:
# * add version
# * create man page using help2man
# * log errors somewhere, now that I'm as quiet as possible

# TODO move prints out of class (as much as possible)

# Imports ---------------------------------------------------------------------
from threading import Thread
import argparse
import errno
import operator
import os
import os.path
import shutil
import subprocess
import sys
import tempfile
import time


# Functions -------------------------------------------------------------------
def getDirContentsSize(start_path='.'):
    """Returns the total size of a directory's contents."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        total_size += sum(
            map(os.path.getsize,
                filter(os.path.isfile,
                       map(lambda f: os.path.join(dirpath, f), filenames)
                )
            )
        )

    return total_size


def spaceLeft(path):
    """Returns space left on the device that contains the given path."""
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize


def spaceSavingsPercentage(former_size, compressed_size):
    """Returns 100 * (1 - compression ratio)."""
    return 100 * (1.0 - float(compressed_size) / former_size)


def which(program):
    """Returs True if and only if whether program exists in system path."""
    # (stackoverflow.com/questions/377017/test-if-executable-exists-in-python)
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath and is_exe(program):
        return True

    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, program)
        if is_exe(exe_file):
            return True

    return False


class CompressorThread(Thread):
    """Thread in charge of compressing files."""
    def __init__(self, controller, basename, program, filename):
        """Set up this thread."""
        Thread.__init__(self)
        self.controller = controller
        self.basename = basename
        self.program = program
        self.filename = filename
        #self.target = target
        self.setDaemon(False)  # TODO check that I actually want this

    def run(self):
        """Carry out the compression."""
        command = [self.program]
        output_filename = os.path.join(self.controller.workdir,
            ".".join([self.basename, self.controller.extensions[self.program]])
        )

        if self.program in ["bgzip", "bzip2", "gzip", "lzip", "lzop", "xz"]:
            command += self.controller.compressor_options[self.program] \
                     + [self.filename]
            try:
                outfile = open(output_filename, "w")
                subprocess.call(command, stdout=outfile, stderr=None)
                outfile.close()
            except subprocess.CalledProcessError as e:
                print(e.output)
                return -1

        elif self.program == "kgb":
            command += self.controller.compressor_options[self.program] \
                     + [output_filename, self.filename]
            try:
                subprocess.check_output(command)
            except subprocess.CalledProcessError as e:
                print(e.output)
                return -1

        elif self.program == "rzip":
            command += self.controller.compressor_options[self.program] \
                     + [self.filename]
            command += ["-o", output_filename]
            try:
                subprocess.call(command)
            except subprocess.CalledProcessError as e:
                print(e.output)
                return -1

        elif self.program == "p7zip":
            # BUG: p7zip fails when we don't have write access to dir, fix
            # it
            # p7zip does not allow us to keep the file, so we back it
            # up first
            if self.controller.original_dir_writable:
                try:
                    bak = os.path.join(self.controller.workdir,
                                       ".".join([self.filename, "bak"]))
                    shutil.copy(self.filename, bak)
                    command += self.controller.compressor_options[self.program]
                    command += [self.filename]
                    subprocess.check_output(command)  # call p7zip quietly
                    # restore copy
                    shutil.move(bak, self.filename)
                    output_filename = ".".join([
                        self.filename, self.controller.extensions[self.program]
                    ])

                except subprocess.CalledProcessError as e:
                    print(e.output)
                    return -1

            else:  # TODO find a way to compress
                print("\t[p7zip]: Cannot output archive to original "
                        "directory, skipping ...")
                return -1

        elif self.program in ["rar", "zip", "zpaq"]:
            if self.program == "rar":  # special processing
                command += ["a"]

            command += self.controller.compressor_options[self.program] \
                     + [output_filename, self.filename]
            try:
                subprocess.check_output(command)  # call program quietly

            except subprocess.CalledProcessError as e:
                print(e.output)
                return -1

        else:
            print("[WARNING] Unsupported program", self.program, "\b, "
                    "skipping...")
            return -1

        # save size for comparison and path in order to be able to delete
        # the archive (possibly); if a program fails for any reason, the
        # reported size will be 0, which is not possible, so we avoid
        # problems by ignoring the file
        current_size = os.path.getsize(output_filename)
        if current_size:
            self.controller.archives.append((os.path.abspath(output_filename),
                                    current_size))
            if current_size < self.controller.smallest_size:
                self.controller.best_program = self.program
                self.controller.smallest_size = current_size

        else:
            print("[WARNING]", self.program, "produced an empty archive, "
                    "removing it...")
            os.remove(output_filename)

        self.controller.finished_threads[self.program] = 1


# The Squeezer class, which will basically do all the work --------------------
class Squeezer:
    # TODO error codes (file not found, wrong permissions, etc.)
    # TODO: doc string "description"
    # compressors to look for
    compressors = ["bgzip", "bzip2", "gzip", "kgb", "lzip", "lzop", "p7zip",
                   "rar", "rzip", "xz", "zip", "zpaq"]

    existing_compressors = []

    # options for each compressor; see each program's man page for more
    # information. Basically, I selected the options that resulted in the best
    # compression
    compressor_options = {"bgzip": ["-c"],
                          "bzip2": ["--best", "--keep", "-c"],
                          "gzip":  ["--best", "-c"],
                          "kgb":   ["-9"],
                          "lzip":  ["--best", "--keep", "-q", "-c"],
                          "lzop":  ["-9", "-c"],
                          "p7zip": [""],
                          "rzip":  ["--best", "--keep"],
                          "rar":   ["-s", "-m5", "-id"],
                          "xz":    ["-e", "--keep", "-9", "-c"],
                          "zip":   ["-9", "-q"],
                          "zpaq":  ["qc"]}

    # store extensions for each compressor
    extensions = {"bgzip": "bgzip",
                  "bzip2": "bz2",
                  "gzip":  "gz",
                  "kgb":   "kgb",
                  "lzip":  "lz",
                  "lzop":  "lzo",
                  "p7zip": "7z",
                  "rar":   "rar",
                  "rzip":  "rz",
                  "xz":    "xz",
                  "zip":   "zip",
                  "zpaq":  "zpaq"}

    # monitored finished threads
    finished_threads = dict.fromkeys(compressors, 0)

    def __init__(self):
        self.mode = "file"   # whether we are compressing a file or a directory
        self.keep = False                # keep (or not) all generated archives
        self.blacklist = []                            # compressors to exclude
        self.detectCompressors()
        if which("zpaq"):
            self.tweakZpaq()

        # create work directory
        self.workdir = os.path.join(tempfile.gettempdir(), "squeeze")
        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)

        # keep track of whether we can write to the directory that contains the
        # file(s) to compress
        self.original_dir_writable = True

        # keep track of paths to created archives (some archivers do not allow
        # us to store them where we please)
        self.archives = []

    def detectCompressors(self):
        """Scans the system for installed compression programs and stores
        them."""
        self.existing_compressors = list(filter(which, self.compressors))

    def makeTarball(self, filename):
        """Creates a tarball in the work directory from the given filename."""
        dirname = os.path.basename(filename)
        tarname = os.path.join(self.workdir, ".".join([dirname, "tar"]))
        try:
            subprocess.call(["tar", "-cf", tarname, filename])

        except subprocess.CalledProcessError as e:
            print(e.output)
            return ""

        return os.path.abspath(tarname)

    def removeArchives(self, s):
        """Removes all generated archives whose base name is filename and whose
        size is larger than s."""
        for (archive, size) in self.archives:
            # check that archive exists (may not be the case since this method
            # is already called as we compress) and remove it if its size
            # exceeds s
            if os.path.isfile(archive) and size > s:
                os.remove(archive)

    def setCompressorsToExclude(self, blacklist):
        """Sets the compressors to exclude."""
        if blacklist is not None:
            self.blacklist = blacklist

    def setKeepArchives(self, value):
        """Sets the flag indicating whether all archives should be kept."""
        self.keep = value

    def tweakZpaq(self):
        """Search for max.cfg if available and set options accordingly."""
        # this is the path to max.cfg on mint and ubuntu
        ubuntu_cmax_path = "/usr/share/doc/zpaq/examples/max.cfg"
        if os.path.exists("max.cfg"):
            self.compressor_options["zpaq"] = ["qcmax.cfg"]
        elif os.path.exists(ubuntu_cmax_path):
            self.compressor_options["zpaq"] = ["qc" + ubuntu_cmax_path]
        # TODO handle other OS's? use built-in stuff to detect the OS
        # TODO ask user if he wants to download the file?

    def compress(self, filename):
        """Do the actual compression."""
        # clean up the path to the wanted filename
        filename, original_filename = [os.path.abspath(filename)] * 2

        # check file existence and permissions
        if not os.path.exists(filename):
            return errno.ENOENT

        if not os.access(filename, os.R_OK):
            # TODO the safe way (http://docs.python.org/2/library/os.html)
            return errno.EACCES

        # check that the directory that contains the file to compress is
        # writable
        self.original_dir_writable = os.access(os.path.split(filename)[0],
                                               os.W_OK)

        # check mode (whether we're compressing a file or a directory)
        self.mode = ["file", "dir"][os.path.isdir(filename)]

        if self.mode == "dir":
            self.original_size = getDirContentsSize(filename)
            filename = self.makeTarball(filename)

        else:
            self.original_size = os.path.getsize(filename)

        if filename == "":
            print("Empty filename, aborting.")
            exit(-1)

        basename = os.path.basename(filename)

        # try every compressor and discard all archives except the smallest one
        self.smallest_size = sys.maxsize
        self.best_program = ""
        num_compressors = len(self.existing_compressors)
        for (i, program) in enumerate(self.existing_compressors):
            if program not in self.blacklist:
                CompressorThread(self, basename, program, filename).start()

        # waiting for threads to finish:
        p = sum(self.finished_threads.values())
        k = len(self.finished_threads) - len(self.blacklist)
        while p < k:
            print("Waiting for", k - p, ["threads", "thread"][k - p == 1],
                  "to finish...", end="\r")
            sys.stdout.flush()
            time.sleep(1)
            p = sum(self.finished_threads.values())

        if self.smallest_size >= self.original_size:
            print("No compressor was able to decrease the size of your file")
            # clean up
            if not self.keep:
                self.removeArchives(0)

        elif not self.keep:
            # delete all archives except the smallest one
            # TODO what do we choose if several archives have exactly the
            # same smallest size?
            self.removeArchives(self.smallest_size)
            if self.mode == "dir":  # delete tarball
                os.remove(filename)

        # move the produced archive to its final location
        final_path = os.path.split(original_filename)[0]
        best_archive = ".".join([basename, self.extensions[self.best_program]])
        if self.original_dir_writable:
            shutil.move(os.path.join(self.workdir, best_archive),
                        os.path.join(final_path, best_archive))

        else:
            print("\nCannot move best archive to", final_path, "because it is"
                  " not writable; you will find it in", self.workdir)

        return 0

# End of the Squeezer class ---------------------------------------------------

if __name__ == "__main__":
    # creating the parser
    parser = argparse.ArgumentParser(
        prog='squeeze',
        description='Compresses a file using the best available program.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    # positional arguments
    parser.add_argument('filename', type=str, help='the path to the file to '
                                                   'compress')

    # optional arguments
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep all generated archives')

    parser.add_argument('-x', '--exclude', type=str, metavar='N', nargs='+',
                        help="compressors to exclude")

    # parse arguments
    args = parser.parse_args()

    S = Squeezer()
    S.setCompressorsToExclude(args.exclude)

    # list installed compressors
    print("The following compressors were found:")
    for prog in S.compressors:
        print("\t", [" x ", " v "][prog in S.existing_compressors].join("[]"),
              prog, ["", "\t(will be ignored)"][prog in S.blacklist])

    # set options and do the work
    S.setKeepArchives(args.keep)
    rc = S.compress(args.filename)
    if rc:  # something went wrong, tell user
        print(os.strerror(rc))

    print("\nBest compression achieved by", S.best_program,
          "\b, achieving a compressed size\nof", S.smallest_size, "bytes "
          "(savings:", "{0:.2f}".format(spaceSavingsPercentage(S.original_size,
                                        S.smallest_size)), "%)")

    # display savings achieved by the other programs in percentages
    print("\nHere's what the other programs did:")
    S.archives = sorted([(archive, size) for archive, size in S.archives
                         if os.path.splitext(archive)[1][1:]
                         != S.extensions[S.best_program]],
                        key=operator.itemgetter(1))

    for (archive, size) in S.archives:
        print("\t", os.path.splitext(archive)[1][1:], "\t:", size, "(savings:",
              "{0:.2f}".format(spaceSavingsPercentage(S.original_size, size)),
              "%)")
