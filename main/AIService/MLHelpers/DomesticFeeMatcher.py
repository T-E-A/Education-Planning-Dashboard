import joblib
import logging
import inspect
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Loads the domestic fee matcher model pkl to find the optimal choice for domestic students
BASE_DIR = Path(__file__).resolve().parent.parent


model_path = Path(
    os.getenv(
        "Domestic_Fee_Matcher",
        (BASE_DIR.parent / "Repository"/ "ModelPackages" /"domestic_fees_matcher.pkl")
    )
).resolve()

logger.info(f"Using PKL: {model_path}")

class DomesticFeeMatcher:
      
    def __init__(self):
        '''
            Initializes the DomesticFeeMatcher instance.
        '''
        try:
            self.className = self.__class__.__name__ # stores class name for error logs
            
            # placeholders - will be filled by Initialize()
            self.nn = None # KNN Model 
            self.scaler = None # Scaler used to normalize student input
            self.universityids = None # list of NOC jobs the model knows about 

            self.Initialize()

        except Exception as e:
             logger.exception(e)
    
    def Initialize(self):
        '''
            Initializes the DomesticFeeMatcher instance.
        '''
        
        try:
            data = joblib.load(model_path) # load the pre-trained model package

            # unpack the three components saved inside the file 
            nn = data["model"]  # the trained KNN model 
            scaler = data["scaler"] # Scaler to normalize incoming student input 
            universityids = data["universityids"] # the universityids the model was trained on

            self.nn = nn
            self.scaler = scaler
            self.universityids = universityids

        except Exception as e:
             logger.exception(e)
    
    def Get_Universities(self, user_input: list[int]):
        '''
            Retruns: a list of the best matching universities for the given student input for domestic fee matching
            args:
                user_input: a list of integers representing the student's input features
        '''
        try:
            user_input_scaled = self.scaler.transform([user_input]) # normalize the students input so it matches the scale the model expects
            _, indices = self.nn.kneighbors(user_input_scaled) # ask the KNN model for the nearest matching jobs; we only need the incides

            # use the indices to look up and return the actual universityids
            return self.universityids.iloc[indices[0]].tolist()

        except Exception as e:
            logger.exception(e)