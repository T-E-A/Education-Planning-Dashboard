
Program_Post_Grad_Employment_Rate_Dict = {
    1: '2020 Employment Rate 6 Months after Graduation',
    2: '2020 Employment Rate 2 Years after Graduation',
    3: '2020 Graduation Rate',
}

Program_Post_Grad_Employment_Rate_Dict_All = {
    1: 'Employment Rate 6 Months after Graduation',
    2: 'Employment Rate 2 Years after Graduation',
    3: 'Graduation Rate',
}


Pathways_Routes = {
    1: 'Field of Study ➡️ Career',
    2: 'Career ⬅️ Field of Study',
}

Pathways_Agg_Operation ={
    1: 'MajorFieldOfStudyParent',
    2: 'BroadCategory'
}


Domestic_Or_International = {
    1 : 'Domestic',
    2: 'International',
}


def Generate_Options(KeyDict, *,errorMessage=None):
    try:

        if errorMessage:
            return [
            {
                'label': f"⚠️ Error loading options => {str(errorMessage)}",
                'value': 'ERROR'
            }
        ]

        Options = [
            {'label': val, 'value': choice}
            for choice, val in KeyDict.items()
        ]

        return Options

    except Exception as e:
        # Fallback option (keeps Dash component stable)
        return [
            {
                'label': f"⚠️ Error loading options => {str(e)}",
                'value': 'ERROR'
            }
        ]


