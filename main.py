#!/usr/bin/env python

class System:
	pass

class LinearSystem(System):
	def __init__(self, equations):
		self.equations = equations

	def __str__(self):
		eqsStr = []

		greaterEqualSignPos = 0
		for eq in self.equations:
			eqStr = str(eq)

			equalSignPos = eqStr.find('=')
			if equalSignPos > greaterEqualSignPos:
				greaterEqualSignPos = equalSignPos

			eqsStr.append(eqStr)

		# Sexy printing
		i = 0
		for eqStr in eqsStr:
			equalSignPos = eqStr.find('=')
			eqStr = ' '*(greaterEqualSignPos - equalSignPos) + eqStr
			eqsStr[i] = eqStr
			i += 1

		return '\n'.join(eqsStr)

	def __len__(self):
		return len(self.equations)

	def __iter__(self):
		return iter(self.equations)

	def __getitem__(self, key):
		return self.equations[key]

	def __reversed__(self):
		return LinearSystem(reversed(self.equations))

	def pivot(self):
		allNull = True
		for eq in self.equations:
			if len(eq):
				allNull = False
				break

		if allNull:
			return self

		pivot = None
		pivotCoeff = None
		pivotEq = None
		for eq in self.equations:
			for letter in eq:
				if not letter: continue

				coeff = eq[letter]

				if pivotCoeff is None or abs(coeff) < abs(pivotCoeff):
					pivotCoeff = coeff
					pivot = letter
					pivotEq = eq

		eqs = []
		for eq in self.equations:
			if eq is pivotEq: continue

			if pivot in eq:
				eqPivotCoeff = eq[pivot]
			else:
				eqPivotCoeff = 0

			eq *= pivotCoeff
			eqPivotEq = pivotEq * eqPivotCoeff

			eqs.append(eqPivotEq - eq)

		if len(eqs) > 1:
			subsys = LinearSystem(eqs)
			eqs = subsys.pivot().equations
		eqs.insert(0, pivotEq)

		return LinearSystem(eqs)

	def solve(self):
		reducedSys = reversed(self.pivot())

		found = {}
		for eq in reducedSys:
			result = eq.solve(found)

			if result == False:
				return False
			elif isinstance(result, dict):
				for letter in result:
					if letter in found:
						if found[letter] != result[letter]:
							return False
					else:
						found[letter] = result[letter]

		return found

class Equation:
	pass

class LinearEquation(Equation):
	def __init__(self, data):
		self.data = {}

		if isinstance(data, dict):
			self.fromCoeff(data)
		elif isinstance(data, str):
			self.fromStr(data)

	def fromCoeff(self, data):
		self.data = {}

		for letter in data:
			coeff = data[letter]
			if coeff == 0:
				continue
			self.data[letter] = coeff

	def fromStr(self, string):
		eqData = { '': 0 }

		coeff = ''
		is2ndMember = False

		def coeffToInt(coeff):
			if coeff in ['+', '-']:
				coeff += '1'

			if coeff == '':
				coeff = 1
			else:
				coeff = int(coeff)

			if is2ndMember:
				coeff = -coeff
			return coeff

		for char in string:
			if char.isdigit():
				coeff += char
			elif char in ['+', '-']:
				coeff = char
			elif char == '=':
				if coeff:
					eqData[''] = coeffToInt(coeff)
					coeff = ''
				is2ndMember = True
			elif char.isalpha() or char == '':
				eqData[char] = coeffToInt(coeff)
				coeff = ''

		if coeff:
			coeff = coeffToInt(coeff)
			eqData[''] += coeff

		return self.fromCoeff(eqData)

	def solve(self, found = {}):
		unknown = None
		value = 0
		for letter in self:
			if letter == '':
				value = - self[letter]
			elif letter in found:
				value -= self[letter] * found[letter]
			else:
				if unknown is None:
					unknown = letter
				else:
					raise Exception('More than one unknown')

		if unknown is None:
			return (value == 0)
		else:
			return { unknown: value / self[unknown] }

	def __len__(self):
		return len(self.data.keys())

	def __str__(self):
		string = ''

		for letter in self:
			coeff = self[letter]

			if coeff < 0: string += '- '
			elif string: string += '+ '
			string += str(abs(coeff))+letter+' '

		if not string: string = '0 '
		return string + '= 0'

	def __iter__(self):
		return iter(self.data)

	def __getitem__(self, key):
		return self.data[key]

	def __mul__(self, factor):
		data = {}
		for letter in self:
			data[letter] = self[letter] * factor
		return LinearEquation(data)

	def __add__(self, other):
		data = {}

		for letter in self:
			coeff = self[letter]

			if letter in other:
				data[letter] = coeff + other[letter]

		for letter in other:
			coeff = other[letter]

			if letter in self: continue

			data[letter] = coeff

		return LinearEquation(data)

	def __neg__(self):
		return self * (-1)

	def __sub__(self, other):
		return self + (-other)

print('Entrez le système :')

eqs = []
while True:
	eqStr = input()

	if not eqStr:
		break
	else:
		eqs.append(LinearEquation(eqStr))

sys = LinearSystem(eqs)
print(str(sys.solve()))