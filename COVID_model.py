import turtle
import numpy as np
import matplotlib.pyplot as plt
import random

wn = turtle.Screen()
wn.bgcolor("black")
wn.title("Epidemic Model")

def decision(probability):    #this function returns true or false based on a probability.
    return random.random() < probability #random.random() prints a random floating point value between 0 and 1

def rand(x,y): # returns random number between x and y-1
    return np.random.randint(x,y)

#vaccines
vaccinated = 0
need_vaccine = vaccinated
vaccine_rollout = 30
v = 0

#population stats
population = 100
infected = 20
Dead = 0
recovered = 0
susceptible = population - infected

#simulation parameters
simulation_cycles = 30
movement_speed = 0     # 0 = max speed
distance_per_cycle = 10 
Infected_arrival_chance = 0
max_potential_infected_visitors = 10
population_spread = 20  #25 max

#covid stats
infection_distance = 30
infectiosness = 0.8 #probability of transmitting it if in range
recovery_chance = 0.2    #this is the chance you will recover if you have been infected for longer than the min_recovery_time (next variable)
min_recovery_time = 5
Covid_mortality = 0.01
Mortality_after_infection = 0.001 
Mortality_after_vaccination = 0.0005
Mortality_after_infection_and_vaccination = 0.0001
Death_clock = 20
Full_immunity_period = 14 #the time you are fully immune from reinfection after recovering
Immunity_after_infection = 1
Immunity_after_vaccination = 0.92
Immunity_after_infected_and_vaccinated = 0.97
Immunity_decrease_per_cycle = 0.002

#lockdown
lockdown_threshold = 1 #percentage of population infected that will initiate a lockdown
social_distance_factor = 1 #social distance factor of 1 means perfect social distancing, the distance between each person is always greater than the infection distance


class Ball(turtle.Turtle): #A ball represents a human in our simulation
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.shape("circle")
        self.color()
        self.penup()
        self.speed(0)
        self.goto(rand(-9,10)*population_spread,rand(-9,10)*population_spread)
        self.infected_time = 0
        self.immunity = 0
        self.vaccinated = False
        self.times_infected = 0
        self.infectiosness = infectiosness
        self.mortality = Covid_mortality
        self.time_since_last_infection = 0
        self.survives = 3 

P=[] #list containing all objects in simulation


infected_log = [infected]
susceptible_log = [susceptible]
recovered_log = [0]
sim_log = [0]

print(infected_log,susceptible_log)

for i in range(population-infected):
    i = Ball()
    i.color("green")
    P.append(i)

for i in range(infected):
    i = Ball()
    i.color("red")
    P.append(i)

for x in range(simulation_cycles):
    if decision(Infected_arrival_chance):
        for z in range(rand(1,max_potential_infected_visitors + 1)): 
            z = Ball()
            z.color("red")
            P.append(z)
            population += 1
            infected += 1
            
    for i in P:
            i.speed(movement_speed) 
            i.goto(i.xcor() + rand(-1,2)*distance_per_cycle,i.ycor() + rand(-1,2)*distance_per_cycle)
    for j in P: 
            if j.color() == ("red","red"):
                    for k in P: #this for loop causes infection via community transmission. 
                        if (k.times_infected > 0 and k.time_since_last_infection <= Full_immunity_period) == False: #If the ball been recovered for less time than the full immunity period, it will not be able to get infected
                            if k.color() == ("green","green") and (j.xcor()-k.xcor())**2 + (j.ycor()-k.ycor())**2 < infection_distance**2 and decision(k.infectiosness): 
                                  k.color("red")
                                  k.mortality = Covid_mortality
                                  k.infected_time = 0 #whenever someone is infected, their infected time is reset to 0
                                  infected += 1
                                  susceptible -= 1
                            if k.color() == ("yellow","yellow") and (j.xcor()-k.xcor())**2 + (j.ycor()-k.ycor())**2 < infection_distance**2 and decision(k.infectiosness): 
                                    if decision(1-k.immunity):
                                        k.color("red")
                                        infected += 1
                                        susceptible -= 1 
                                        k.infected_time = 0
                                        if k.times_infected == 0:
                                            k.mortality = Mortality_after_vaccination
                                        else: 
                                            k.mortality = Mortality_after_infection_and_vaccination
                        
                            if k.color() == ("blue","blue") and (j.xcor()-k.xcor())**2 + (j.ycor()-k.ycor())**2 < infection_distance**2 and decision(k.infectiosness):
                                    if decision(1-k.immunity):
                                        k.color("red")
                                        k.mortality = Mortality_after_infection
                                        infected += 1
                                        susceptible -= 1
                                        k.infected_time = 0
                                        
            #survival determiner
            if j.survives == 3:  #j.survives will be 3 if the survival of the person has not yet been decided, if the survival has already been determined, then j.survives will equal either 1 or 0.
                if j.color() == ("red", "red"): #if the person is infected, the person's survival will be predetermined and set to either 1 or 0, 1 meaning the person survives. 
                    if decision(1-k.mortality): 
                        j.survives = 1
                    else:
                        j.survives = 0      
                
            if j.times_infected > 0:
                j.time_since_last_infection += 1 
            if j.color() == ("red","red"):
                j.time_since_last_infection = 0
                j.infected_time += 1
                
            if j.immunity > 0: 
                j.immunity -= Immunity_decrease_per_cycle
                if j.immunity < 0:
                    j.immunity = 0
            
                    
            if j.color() == ("red","red") and j.survives == 1:
                if decision(recovery_chance) and j.infected_time >= min_recovery_time: 
                    if j.vaccinated:
                        j.color("yellow")
                    else:
                        j.color("blue")
                    if j.times_infected > 0 and j.vaccinated:
                        j.immunity = Immunity_after_infected_and_vaccinated
                    else:
                        j.immunity = Immunity_after_infection
                    j.times_infected += 1
                    j.time_since_last_infection = 0
                    recovered += 1
                    infected -= 1
                    j.survives = 3 #if the person recovers, his survivability is 'reset' so that if the person is infected again, his survivability will be determined once more by probability.
                    
                            
            else:
                if j.infected_time >= Death_clock and j.color() == ("red", "red"):
                    j.color("grey")
                    j.speed(0)
                    P.remove(j)
                    population -= 1
                    infected -= 1
                    Dead += 1
                    if j.vaccinated:
                        v -= 1
        
    if x >= vaccine_rollout and need_vaccine > 0:
        for i in P:
            if (i.color() == ("green","green") or i.color() == ("blue","blue")) and need_vaccine > 0:
                i.color("yellow")
                i.immunity = Immunity_after_vaccination
                i.vaccinated = True
                need_vaccine -= 1
                v += 1

    infected_log.append(infected)
    susceptible_log.append(susceptible)
    recovered_log.append(recovered)
    sim_log.append(sim_log[-1] + 1)
    print("cycle:",sim_log[-1])
    print("S =",susceptible,"I =",infected,"R =",recovered, "P =", population, "D =", Dead, "V =", v)

plt.plot(sim_log,infected_log,label = "infected",color = "red")
plt.plot(sim_log,susceptible_log,label = "susceptible",color = "green")
plt.plot(sim_log,recovered_log,label = "recovered", color = "blue")
plt.legend()
plt.show()

