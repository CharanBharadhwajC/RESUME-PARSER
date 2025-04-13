import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def compute_fuzzy_priority(skills, experience, education):
    # Define fuzzy variables
    skills_input = ctrl.Antecedent(np.arange(0, 11, 1), 'skills')
    experience_input = ctrl.Antecedent(np.arange(0, 11, 1), 'experience')
    education_input = ctrl.Antecedent(np.arange(0, 11, 1), 'education')
    priority_output = ctrl.Consequent(np.arange(0, 11, 1), 'priority')

    # Membership functions for skills
    skills_input['low'] = fuzz.trimf(skills_input.universe, [0, 0, 5])
    skills_input['medium'] = fuzz.trimf(skills_input.universe, [0, 5, 10])
    skills_input['high'] = fuzz.trimf(skills_input.universe, [5, 10, 10])

    # Membership functions for experience
    experience_input['low'] = fuzz.trimf(experience_input.universe, [0, 0, 5])
    experience_input['medium'] = fuzz.trimf(experience_input.universe, [0, 5, 10])
    experience_input['high'] = fuzz.trimf(experience_input.universe, [5, 10, 10])

    # Membership functions for education
    education_input['low'] = fuzz.trimf(education_input.universe, [0, 0, 5])
    education_input['medium'] = fuzz.trimf(education_input.universe, [0, 5, 10])
    education_input['high'] = fuzz.trimf(education_input.universe, [5, 10, 10])

    # Membership functions for priority
    priority_output['low'] = fuzz.trimf(priority_output.universe, [0, 0, 5])
    priority_output['medium'] = fuzz.trimf(priority_output.universe, [0, 5, 10])
    priority_output['high'] = fuzz.trimf(priority_output.universe, [5, 10, 10])

    # Define fuzzy rules
    rule1 = ctrl.Rule(skills_input['high'] & experience_input['high'] & education_input['high'], priority_output['high'])
    rule2 = ctrl.Rule(skills_input['medium'] & experience_input['medium'] & education_input['medium'], priority_output['medium'])
    rule3 = ctrl.Rule(skills_input['low'] | experience_input['low'] | education_input['low'], priority_output['low'])

    # Control system
    priority_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    priority_sim = ctrl.ControlSystemSimulation(priority_ctrl)

    # Input values
    priority_sim.input['skills'] = skills
    priority_sim.input['experience'] = experience
    priority_sim.input['education'] = education

    # Compute the result
    priority_sim.compute()
    score = priority_sim.output['priority']
    return round(score, 2)
