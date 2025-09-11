import sys
# import numpy as np
# import pandas as pd
# from sklearn import ...
inputstr = []
strtots = ""
for line in sys.stdin:
    #discovered a newline character so needed to get rid of it in each input line
    #combining both input lines into one array to make it easier to discover sets
    strtots += line[0:-1] + " "

#Splitting each character from combined string
x = strtots.split(" ")
#This sort ensures that all the similar values are grouped together in order
x.sort()

outputstr=""
counter = 0
while(counter+1<len(x)):
    #Each contiguous pair of values are compared to check for similarity
    #if discovered, instead of checking next value, the counter is incremented to check next pair
    if(x[counter]==x[counter+1]):
        outputstr += x[counter] + " "
        counter += 2
    else:
        counter += 1


#checking if the loop returned an empty string to display output
if(outputstr != ""):
    #getting rid of final space added in the loop
    print(outputstr[:-1])
else:
    print("NULL")