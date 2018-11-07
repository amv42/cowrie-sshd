# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.

"""
This module ...
"""

from __future__ import absolute_import, division

import getopt

from cowrie.shell.command import HoneyPotCommand

commands = {}

FREE_OUTPUT = """              total        used        free      shared  buff/cache   available
Mem:{MemTotal:>15}{calc_total_used:>12}{MemFree:>12}{Shmem:>12}{calc_total_buffers_and_cache:>12}{MemAvailable:>12}
Swap:{SwapTotal:>14}{calc_swap_used:>12}{SwapFree:>12}
"""


class command_free(HoneyPotCommand):
    """
    free
    """

    def call(self):
        # Parse options or display no files
        try:
            opts, args = getopt.getopt(self.args, 'mh')
        except getopt.GetoptError:
            self.do_free()
            return

        # Parse options
        for o, a in opts:
            if o in ('-h'):
                self.do_free(fmt='human')
                return
            elif o in ('-m'):
                self.do_free(fmt='megabytes')
                return
        self.do_free()

    def do_free(self, fmt='kilobytes'):
        """
        print free statistics
        """

        # Get real host memstats and add the calculated fields
        raw_mem_stats = self.get_free_stats()
        raw_mem_stats['calc_total_buffers_and_cache'] = raw_mem_stats['Buffers'] + raw_mem_stats['Cached']
        raw_mem_stats['calc_total_used'] = raw_mem_stats['MemTotal'] - (
            raw_mem_stats['MemFree'] + raw_mem_stats['calc_total_buffers_and_cache']
        )
        raw_mem_stats['calc_swap_used'] = raw_mem_stats['SwapTotal'] - raw_mem_stats['SwapFree']

        if fmt == 'megabytes':
            # Transform KB to MB
            for key, value in raw_mem_stats.iteritems():
                raw_mem_stats[key] = int(value / 1000)
        elif fmt == 'human':
            magnitude = ["B", "M", "G", "T", "Z"]
            for key, value in raw_mem_stats.iteritems():
                current_magnitude = 0

                # Keep dividing until we get a sane magnitude
                while(value >= 1000 and current_magnitude < len(magnitude)):
                    value = round(float(value / 1000), 1)
                    current_magnitude += 1

                # Format to string and append value with new magnitude
                raw_mem_stats[key] = str("{:g}{}".format(value, magnitude[current_magnitude]))

        # Write the output to screen
        self.write(FREE_OUTPUT.format(**raw_mem_stats))

    def get_free_stats(self):
        """
        Get the free stats from /proc
        """
        needed_keys = ["Buffers", "Cached", "MemTotal", "MemFree", "SwapTotal", "SwapFree", "Shmem", "MemAvailable"]
        mem_info_map = {}
        with open('/proc/meminfo', 'r') as proc_file:
            for line in proc_file:
                tokens = line.split(':')

                # Later we are going to do some math on those numbers, better not include uneeded keys for performance
                if tokens[0] in needed_keys:
                    mem_info_map[tokens[0]] = int(tokens[1].lstrip().split(' ')[0])

        # Got a map with all tokens from /proc/meminfo and sizes in KBs
        return mem_info_map


commands['/usr/bin/free'] = command_free
commands['free'] = command_free
