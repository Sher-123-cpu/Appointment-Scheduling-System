
class Triage:
    
    @staticmethod
    def triagelevel(L1_responses,L2_responses,L3_responses,L4Responses):
        for response in L1_responses:
            if response == 'Yes':
                return 1
        for response in L2_responses:
            if response == 'Yes':
                return 2
        level =  Triage.determine_triage_level345(L3_responses)
        if level == 3:
            if Triage.has_danger_zone_vitals(L4Responses[0],L4Responses[1]):
                return 2
            else: 
                return 3
        else: 
            return level



    def determine_triage_level345(responses):
        # Initialize counters for each triage level
        triage_3_counter = 0
        triage_4_counter = 0
        triage_5_counter = 0
        if len(responses) == 0:
            return 5
    
        # Evaluate responses to the questions
        for response in responses:
            if response == "Yes Multiple":
                triage_3_counter += 1
            elif response == "Yes But Just One":
                triage_4_counter += 1
            elif response == "None":
                triage_5_counter += 1
    
        # If all responses indicate a single resource, consider as Triage Level 3
        if triage_4_counter > 1:
            triage_3_counter += triage_4_counter
            triage_4_counter = 0
    
        # Determine the triage level
        if triage_3_counter > 0:
            return 3
        elif triage_4_counter > 0 and triage_3_counter == 0:
            return 4
        elif triage_5_counter == len(responses):
            return 5



    
        

    def has_danger_zone_vitals(age, vitals):
        # Define normal and danger zone ranges for each vital sign
        threem_normal_ranges = {
            'cystolic_blood_pressure': (60, 90),  # Example: (systolic, diastolic) in mmHg
            'diastolic_blood_pressure': (40, 60),  # Example: (systolic, diastolic) in mmHg
            'heart_rate': (100, 180),       # Example: beats per minute (bpm)
            'respiratory_rate': (12, 50),  # Example: breaths per minute (bpm)
            'temperature': (36.1, 38),   # Example: degrees Celsius
            'oxygen_saturation': (92, 100) # Example: percentage (%)
        }

        threem_threeyr_normal_ranges = {
            'cystolic_blood_pressure': (85, 100),  # Example: (systolic, diastolic) in mmHg
            'diastolic_blood_pressure': (55, 70),  # Example: (systolic, diastolic) in mmHg
            'heart_rate': (98, 160),       # Example: beats per minute (bpm)
            'respiratory_rate': (12, 40),  # Example: breaths per minute (bpm)
            'temperature': (36.1, 39),   # Example: degrees Celsius
            'oxygen_saturation': (92, 100) # Example: percentage (%)
        }
        threeyr_eightyr_normal_ranges = {
            'cystolic_blood_pressure': (95, 110),  # Example: (systolic, diastolic) in mmHg
            'diastolic_blood_pressure': (60, 75),  # Example: (systolic, diastolic) in mmHg
            'heart_rate': (80, 140),       # Example: beats per minute (bpm)
            'respiratory_rate': (12, 30),  # Example: breaths per minute (bpm)
            'temperature': (36.1, 41),   # Example: degrees Celsius
            'oxygen_saturation': (92, 100) # Example: percentage (%)
        }
        eightyr_normal_ranges = {
            'cystolic_blood_pressure': (100, 120),  # Example: (systolic, diastolic) in mmHg
            'diastolic_blood_pressure': (65, 75),  # Example: (systolic, diastolic) in mmHg
            'heart_rate': (60, 100),       # Example: beats per minute (bpm)
            'respiratory_rate': (12, 20),  # Example: breaths per minute (bpm)
            'temperature': (36.1, 41),   # Example: degrees Celsius
            'oxygen_saturation': (92, 100) # Example: percentage (%)
        }

        if age <= 3:
            normal_ranges = threem_normal_ranges
        elif age <=36:
            normal_ranges = threem_threeyr_normal_ranges
        elif age <=96:
            normal_ranges = threeyr_eightyr_normal_ranges
        else: 
            normal_ranges = eightyr_normal_ranges


        if len(vitals) == 0:
            return False
        for vital, value in vitals.items():
            normal_range = normal_ranges.get(vital)
            if normal_range:
                if value < normal_range[0] or value > normal_range[1]:
                        return True  # Found a vital sign in the danger zone
        return False  # No vital sign found in the danger zone
