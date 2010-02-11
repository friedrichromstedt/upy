# Maintainer: Friedrich Romstedt <friedrichromstedt@gmail.com>
# Copyright 2008 Friedrich Romstedt
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# $Last Changed: 2008 Aug 4$
# Developed since: Aug 2008
# Version: 0.1.0b

import math

Infinity=None

def get_exponent(number):
	"""The position of the first counting digit of some `number' in decimal representation (not exponential). A position of zero means, that the first counting digit is the digit before the point. Nonnegative positions are before the point. Negative positive positions are behind the point.
	
	The number may be multiplied by 10**(-exponent). The first counting digit of the multiplied number is the digit before the point."""	
	if number==0.0:
		return Infinity
	number=abs(number)
	exponent=0
	while round((number-number%(10**exponent))*10**(-exponent))==0.0:
		exponent-=1
	while round((number-number%(10**exponent))*10**(-exponent))!=0.0:
		exponent+=1
	exponent-=1
	return exponent

def get_rounded(number,exponent,force_sign=False,ceil=False):
	"""The string of the `number', up to the digit 10**(`exponent'). If `force_sign' is True, a "+" sign will be returned before nonnegative numbers. If `ceil' is True, the number will be ceil'd instead of round'd."""
	if number<0.0:
		number=-number
		stringsign="-"
	elif force_sign:
		stringsign="+"
	else:
		stringsign=""
	if not ceil:
		countingdigitsseries_number=int(round(number*10**(-exponent)))
	else:
		countingdigitsseries_number=int(math.ceil(number*10**(-exponent)))
	countingdigitsseries=str(countingdigitsseries_number)
	if exponent>=0:
		stringdigitsseries=countingdigitsseries+"0"*exponent
		return stringsign+stringdigitsseries
	elif exponent<0:
		stringdigitsseries="0"*(-exponent+1-len(countingdigitsseries))+countingdigitsseries
		stringnumber=stringdigitsseries[:exponent]+"."+stringdigitsseries[exponent:]
		return stringsign+stringnumber
