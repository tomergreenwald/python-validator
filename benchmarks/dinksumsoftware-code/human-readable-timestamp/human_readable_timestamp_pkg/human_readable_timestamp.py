''' module docstring
'''
from datetime import tzinfo, timedelta, datetime

"""
tsf [-dhmsu]
tsf [-dhmsu] --timestamp filename [...filename]
tsf [-dhmsu] --untimestamp filename [...filename]

tsf
# outputs to stdout the timestamp associated with current time
#     2008-05-02_T_01_10z

tsf --timestamp filename-0 [...filename-N]
# Renames all files inserting a timestamp before the filename extension 
# e.g. tsf --timestamp somefile.pdf
#     somefile.pdf ==> somefile.2008-05-02_T_01_10z.pdf
#

tsf --untimestamp filename-0 [...filename-N]
# renames, removing timestamp e.g.
# tsf --untimestamp somefile.2008-05-02_T_01_10z.pdf 
#    somefile.2008-05-02_T_01_10z.pdf ==> somefile.pdf

All times UTC with 24-hour clock
Real close to, but deviant of 8601 <todo> note differences.

Options:
    -d, --day   day resolution,         2008-05-20z
    -h, --hour  hour resolution,        2008-05-20_T_01z
    -m, --min   minute resolution       2008-05-20_T_01_10z
    -s, --sec   second resolution       2008-05-20_T_01_10_18z  [Default]


Keys to the project and why it exists:
    1) Timestamp format was chosen to be human readable and contain no
    characters that get backslashed on a bash command line. Raw output of
    date --utc is virtually unreadable in "ls" output

    2) Timestamp format was chosen to be almost ISO compiliant with all of it's
    advantages (sortable, standards based etc)

    3) Ability to timestamp and unstamp filenames "in mass"

"""

# A UTC class TimeZone
# Taken from tzinfo documentation
class UTC(tzinfo):
    """UTC"""

    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return UTC.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return UTC.ZERO

class HumanReadableTimeStamp :

    # map output_resolution to strftime() format string
    default_output_resolution = 'second'
    format = { 'day'         : '%Y-%m-%dz',
               'hour'        : '%Y-%m-%d_T_%Hz',
               'minute'      : '%Y-%m-%d_T_%H_%Mz',
               'second'      : '%Y-%m-%d_T_%H_%M_%Sz'
             }




    def __init__(self,  when = None, output_resolution = None) :
        self.when = when ;
        self.output_resolution = output_resolution

        # Figure out the moment of time in question
        # We need to get what they gave us to an "aware" datetime in UTC
        if self.when == None :
            # told nothing, use the current time
            self.when = datetime.now(UTC())

        # We have an "aware" datetime in UTC ?
        if isinstance (self.when, datetime) and isinstance(self.when.tzinfo, UTC) :
            pass # yep, life is good
        else :
            # Can't make sense of the moment in time they want
            msg = "Can't make sense of:when:" + repr(self.when)
            raise ValueError( msg )


        # Figure out how many digits to "print out"
        self.strftime_format = None

        # Did user tell us?
        if not self.output_resolution :
            # Nope, use default
            self.output_resolution = HumanReadableTimeStamp.default_output_resolution

        # Is what we have a known key?
        if self.output_resolution in HumanReadableTimeStamp.format :
            # Yep, use it to fetch the format string
            self.strftime_format = HumanReadableTimeStamp.format[self.output_resolution]

        # <todo> Do some smart parsing here, e.g. --second or -s maybe AND
        # put the original in format to speed future lookups (after confirming format is really static)
        else :
            # Can't make sense of output resolution they want
            msg = "Can't make sense of:output_resolution=" + str(self.output_resolution)
            raise ValueError( msg )

    def str(self) : return self.__str__()
    def __str__(self) :
        return  self.when.strftime( self.strftime_format )



                                                                                
