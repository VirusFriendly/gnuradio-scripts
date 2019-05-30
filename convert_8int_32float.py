#!/usr/bin/env python2
import sys
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser

# Converts 8bit unsigned integer IQ data saved by rtlsdr, hackrf, and android "RF Analyzer, into a 32bit float that GQRX and GnuRadio can read

# Note: After writing this I discovered that it was already done in GRC and there were two other ways of converting these file
# https://greatscottgadgets.com/sdr/11/
# But at least I gained some much needed experience with GRC

class top_block(gr.top_block):

    def __init__(self, fname):
        super(top_block, self).__init__()
        self._input_filename = fname
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2400000

        ##################################################
        # Blocks
        ##################################################
        self.blocks_uchar_to_float_1 = blocks.uchar_to_float()
        self.blocks_uchar_to_float_0 = blocks.uchar_to_float()
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, self._input_filename, False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, self._input_filename + '.raw', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_deinterleave_0 = blocks.deinterleave(gr.sizeof_char*1, 1)
        self.blocks_add_const_vxx_1 = blocks.add_const_vff((-127.5, ))
        self.blocks_add_const_vxx_0 = blocks.add_const_vff((-127.5, ))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_add_const_vxx_1, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_deinterleave_0, 0), (self.blocks_uchar_to_float_0, 0))
        self.connect((self.blocks_deinterleave_0, 1), (self.blocks_uchar_to_float_1, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_deinterleave_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_uchar_to_float_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_uchar_to_float_1, 0), (self.blocks_add_const_vxx_1, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)



if __name__ == '__main__':
    if len(sys.argv) > 1:
        tb = top_block(sys.argv[1])
        print "Reading " + sys.argv[1]
        tb.start()
        tb.wait()
        print "Saved as " + sys.argv[1] + ".raw"

