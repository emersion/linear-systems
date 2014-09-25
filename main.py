#!/usr/bin/env python

class System:
	pass

class LinearSystem(System):
	def __init__(self, equations):
		self.equations = equations

	def __str__(self):
		string = ''

		for eq in self.equations:
			string += str(eq)+'\n'

		return string

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

class Equation:
	pass

class LinearEquation(Equation):
	def __init__(self, data):
		self.data = {}

		for letter in data:
			coeff = data[letter]
			if coeff == 0:
				continue
			self.data[letter] = coeff

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

	def __sub__(self, other):
		return self + other*(-1)

	@staticmethod
	def fromStr(string):
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

		return LinearEquation(eqData)

print('Entrez le système :')

eqs = []
while True:
	eqStr = input()

	if not eqStr:
		break
	else:
		eqs.append(LinearEquation.fromStr(eqStr))

sys = LinearSystem(eqs)
print(str(sys.pivot()))