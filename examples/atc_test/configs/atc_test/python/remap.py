#   This is a component of LinuxCNC
#   Copyright 2011, 2012, 2013, 2014 Dewey Garrett <dgarrett@panix.com>,
#   Michael Haberler <git@mah.priv.at>, Norbert Schechner <nieson@web.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import linuxcnc
import traceback

import emccanon
from interpreter import INTERP_OK, INTERP_EXECUTE_FINISH
from util import lineno


throw_exceptions = 1 # raises InterpreterException if execute() or read() fail

def queuebuster(self, **words):
    yield INTERP_EXECUTE_FINISH


def change_prolog(self, **words):
    try:
        if self.selected_pocket < 0:
            return "M6: no tool prepared"

        if self.cutter_comp_side:
            return "Cannot change tools with cutter radius compensation on"

        self.params["tool_in_spindle"] = self.current_tool
        self.params["selected_tool"] = self.selected_tool
        self.params["current_pocket"] = self.current_pocket
        self.params["selected_pocket"] = self.selected_pocket
        return INTERP_OK

    except Exception as e:
        return "M6/change_prolog: {}".format(e)


def change_epilog(self, **words):
    try:
        if self.return_value > 0.0:
            # commit change
            self.selected_pocket =  int(self.params["selected_pocket"])
            emccanon.CHANGE_TOOL(self.selected_pocket)
            # cause a sync()
            self.tool_change_flag = True
            self.set_tool_parameters()
            return INTERP_OK
        else:
            return "M6 aborted (return code {})".format(self.return_value)

    except Exception as e:
        return "M6/change_epilog: {}".format(e)


def prepare_prolog(self, **words):
    try:
        cblock = self.blocks[self.remap_level]
        if not cblock.t_flag:
            return "T requires a tool number"

        tool = cblock.t_number
        if tool:
            (status, pocket) = self.find_tool_pocket(tool)
            if status != INTERP_OK:
                return "T{}: pocket not found".format(tool)
        else:
            pocket = -1 # this is a T0 - tool unload

        # these variables will be visible in the ngc oword sub
        # as #<tool> and #<pocket> local variables, and can be
        # modified there - the epilog will retrieve the changed
        # values
        self.params["tool"] = tool
        self.params["pocket"] = pocket

        return INTERP_OK
    except Exception as e:
        return "T{[t]}/prepare_prolog: {}".format(words, e)


def prepare_epilog(self, **words):
    try:
        if self.return_value > 0:
            self.selected_tool = int(self.params["tool"])
            self.selected_pocket = int(self.params["pocket"])
            emccanon.SELECT_POCKET(self.selected_pocket, self.selected_tool)
            return INTERP_OK
        else:
            return "T%d: aborted (return code %.1f)" % (int(self.params["tool"]),self.return_value)

    except Exception as e:
        return "T%d/prepare_epilog: {}".format(self.selected_tool, e)


def m6(self, **words):
    print("m6 called", words)

    emccanon.SET_AUX_OUTPUT_VALUE(0, 7)
    emccanon.SET_AUX_OUTPUT_BIT(0)

    print("M6 success")

    return INTERP_OK


def m10(self, **words):
    print("m10 called", words)

    return INTERP_OK


def m11(self, **words):
    print("m11 called", words)

    command = linuxcnc.command()
    command.set_digital_output(4, 1)

    return INTERP_EXECUTE_FINISH


def m12(self, **words):
    print("m12 called", words)


    command = linuxcnc.command()
    command.set_digital_output(5, 1)

    return INTERP_EXECUTE_FINISH


def m13(self, **words):
    print("m13 called Homing ATC", words)

    return INTERP_OK


def m21(self, **words):
    print("m21 called", words)

    return INTERP_OK


def m22(self, **words):
    print("m22 called", words)

    return INTERP_OK


def m23(self, **words):
    print("m23 called", words)

    return INTERP_OK


def m24(self, **words):
    print("m24 called")

    return INTERP_OK


def m25(self, **words):
    print("m25 called")

    return INTERP_OK


def m26(self, **words):
    print("m26 called")

    return INTERP_OK
