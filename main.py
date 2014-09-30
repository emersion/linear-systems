#!/usr/bin/env python

import copy

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
	def __init__(self, data = None):
		if isinstance(data, str):
			members = data.split('=')
			firstMember = LinearExpression(members[0])

			if len(members) > 1:
				secondMember = LinearExpression(members[1])
				self.expression = firstMember - secondMember
			else:
				self.expression = firstMember
		else:
			self.expression = LinearExpression(data)

	def __str__(self):
		return str(self.expression) + '= 0'

	def __iter__(self):
		return iter(self.expression)

	def __getitem__(self, key):
		return self.expression[key]

	def __len__(self):
		return len(self.expression)

	def __mul__(self, factor):
		return LinearEquation(self.expression * factor)

	def __add__(self, other):
		if isinstance(other, LinearEquation):
			other = other.expression

		return LinearEquation(self.expression + other)

	def __neg__(self):
		return self * (-1)

	def __sub__(self, other):
		return self + (-other)

	def solve(self, found = {}):
		primaryUnknown = None
		secondaryUnknowns = {}
		value = 0
		for letter in self:
			if letter == '':
				value = - self[letter]
			elif letter in found:
				value = value - found[letter] * self[letter]
			else:
				if primaryUnknown is None:
					primaryUnknown = letter
				else:
					secondaryUnknowns[letter] = - self[letter] / self[primaryUnknown]

		if primaryUnknown is None:
			return (value == 0)
		elif len(secondaryUnknowns) == 0:
			return { primaryUnknown: value / self[primaryUnknown] }
		else:
			# TODO: didnt managed to find a clean way to do this
			# Even with the __div__ magic method
			secondaryUnknowns[''] = value * (1 / self[primaryUnknown])
			return { primaryUnknown: LinearExpression(secondaryUnknowns) }

class Expression:
	pass

class LinearExpression(Expression):
	def __init__(self, data = None):
		self.data = {}

		if isinstance(data, LinearExpression):
			self.fromCoeff(data.data)
		elif isinstance(data, int):
			self.fromCoeff({ '': data })
		elif isinstance(data, dict):
			self.fromCoeff(data)
		elif isinstance(data, str):
			self.fromStr(data)

	def fromCoeff(self, data):
		self.data = {}

		addAfter = None
		if '' in data and isinstance(data[''], LinearExpression):
			addAfter = data['']
			data[''] = 0

		for letter in data:
			coeff = data[letter]
			if coeff == 0:
				continue
			else:
				self.data[letter] = coeff

		if addAfter:
			self.data = (self + addAfter).data

	def fromStr(self, string):
		expData = { '': 0 }

		coeff = ''

		def coeffToInt(coeff):
			if coeff in ['+', '-']:
				coeff += '1'

			if coeff == '':
				coeff = 1
			else:
				coeff = int(coeff)

			return coeff

		for char in string:
			if char.isdigit():
				coeff += char
			elif char in ['+', '-']:
				coeff = char
			elif char.isalpha() or char == '':
				expData[char] = coeffToInt(coeff)
				coeff = ''

		if coeff:
			coeff = coeffToInt(coeff)
			expData[''] += coeff

		return self.fromCoeff(expData)

	def __str__(self):
		string = ''

		for letter in self:
			coeff = self[letter]

			if coeff < 0: string += '- '
			elif string: string += '+ '
			string += str(abs(coeff))+letter+' '

		if not string: string = '0 '

		return string

	def __repr__(self): # TODO: find a way to print solutions of a system without this
		return str(self)

	def __iter__(self):
		return iter(self.data)

	def __getitem__(self, key):
		return self.data[key]

	def __setitem__(self, key, value):
		self.data[key] = value

	def __len__(self):
		return len(self.data.keys())

	def __add__(self, other):
		if not isinstance(other, Expression):
			other = LinearExpression(other)

		expData = copy.copy(self.data)
		for letter in other:
			if not letter in expData:
				expData[letter] = 0

			expData[letter] += other[letter]

		return LinearExpression(expData)

	def __radd__(self, other):
		return self + other

	def __iadd__(self, other):
		return self + other

	def __sub__(self, other):
		return self + (-other)

	def __rsub__(self, other):
		return self - other

	def __isub__(self, other):
		return self - other

	def __mul__(self, other):
		expData = {}
		for letter in self:
			expData[letter] = self[letter] * other
		return LinearExpression(expData)

	def __rmul__(self, other):
		return self * other

	def __neg__(self):
		return self * (-1)

	def __div__(self, other):
		return self * (1 / other)

	def __rdiv__(self, other):
		return (1 / self) * other


if __name__ == '__main__':
	print('Entrez le système :')

	eqs = []
	while True:
		eqStr = input()

		if not eqStr:
			break
		else:
			eqs.append(LinearEquation(eqStr))

	sys = LinearSystem(eqs)
	print(sys.solve())
