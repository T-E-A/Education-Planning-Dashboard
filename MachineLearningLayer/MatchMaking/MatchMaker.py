# Abira Demello

import joblib
import logging
import inspect

# Loads the career matcher model and uses it to find the best NOC job matches for a student based on their input

class Matcher:
   
    def __init__(self):
        method = inspect.currentframe().f_code.co_name
        try:
            self.className = self.__class__.__name__ # stores class name for error logs
            
            # placeholders - will be filled by Initialize()
            self.nn = None # KNN Model 
            self.scaler = None # Scaler used to normalize student input
            self.jobs = None # list of NOC jobs the model knows about 

            self.Initialize()

        except Exception as e:
             logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
    
    def Initialize(self):
        method = inspect.currentframe().f_code.co_name
        try:
            data = joblib.load("career_matcher.pkl") # load the pre-trained model package

            # unpack the three components saved inside the file 
            nn = data["model"]  # the trained KNN model 
            scaler = data["scaler"] # Scaler to normalize incoming student input 
            jobs = data["jobs"] # the job titles the model was trained on

            self.nn = nn
            self.scaler = scaler
            self.jobs = jobs

        except Exception as e:
             logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
    
    def Get_Jobs(self, user_input: list[int]):
        method = inspect.currentframe().f_code.co_name
        try:
            user_input_scaled = self.scaler.transform([user_input]) # normalize the students input so it matches the scale the model expects
            _, indices = self.nn.kneighbors(user_input_scaled) # ask the KNN model for the nearest matching jobs; we only need the incides

            # use the indices to look up and return the actual job titles
            return self.jobs.iloc[indices[0]].tolist()

        except Exception as e:
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
