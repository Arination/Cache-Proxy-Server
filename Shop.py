weight = 41.5
cost = 0

prem_cost = 125

#Ground Shipping
if weight <= 2:
  cost += (weight*1.50) + 20.00
  print("The cost for shipping via Ground = $" + str(cost))
elif 2 < weight <= 6:
  cost += (weight*3.00) + 20.00
  print("The cost for shipping via Ground = $" + str(cost))
elif 6 < weight <= 10:
  cost += (weight*4.00) + 20.00
  print("The cost for shipping via Ground = $" + str(cost))
elif weight > 10:
  cost += (weight*4.75) + 20.00
  print("The cost for shipping via Ground = $" + str(cost))
else:
  print("Please enter valid weight in 'lb'")

##Ground Shipping Premium
print("Cost via Premium = $" + str(prem_cost))

#Drone Shipping
if weight <= 2:
  cost += (weight*4.50)
  print("The cost for shipping via Drone = $" + str(cost))
elif 2 < weight <= 6:
  cost += (weight*9.00)
  print("The cost for shipping via Drone = $" + str(cost))
elif 6 < weight <= 10:
  cost += (weight*12.00)
  print("The cost for shipping via Drone = $" + str(cost))
elif weight > 10:
  cost += (weight*14.25)
  print("The cost for shipping via Drone = $" + str(cost))
else:
  print("Please enter valid weight in 'lb'")