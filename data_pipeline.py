import pandas as pd
import matplotlib as plt
import csv
import re


class DataPipeline:
    """
    A data processing pipeline for employee survey data.

    Usage (once implemented):
        pipeline = DataPipeline("data/messy_employee_survey.csv")
        results = pipeline.run()
    """

    # Canonical spellings for normalization — use these dicts in your clean() method.
    DEPT_MAP = {
        "engineering": "Engineering",
        "eng":         "Engineering",
        "marketing":   "Marketing",
        "mktg":        "Marketing",
        "sales":       "Sales",
        "hr":          "HR",
        "human resources": "HR",
        "h.r.":        "HR",
        "finance":     "Finance",
        "fin":         "Finance",
    }

    LOC_MAP = {
        "new york":        "New York",
        "nyc":             "New York",
        "chicago":         "Chicago",
        "chi":             "Chicago",
        "austin":          "Austin",
        "austin, tx":      "Austin",
        "atx":             "Austin",
        "seattle":         "Seattle",
        "sea":             "Seattle",
        "remote":          "Remote",
        "work from home":  "Remote",
    }

    def __init__(self, filepath):
        """Load the CSV at `filepath` into self.df (a pandas DataFrame).
        Print how many rows and columns were loaded.

        Hint: use pd.read_csv()
        Wrap the load in try/except to catch FileNotFoundError.

        Args:
            filepath: path to the messy CSV file
        """
        self.filepath = filepath # Foundation of the object's state: storing the string filepath that the user entered.
        self.df = None # The DataFrame must live on the object so that all other methods can use it when called (shared state).
        
        # Load the CSV
        try:
            self.df = pd.read_csv(filepath) # Attempt to load the CSV; if successful, df becomes the DataFrame of the user provided filepath.
            print(self.df.shape) # (rows, columns) 
           
        except FileNotFoundError:
            print("File not found. Sorry for the inconvenience. Please try again.") # Error Handling with Grace.
        
                # ✔ Stores filepath
                # ✔ Creates shared DataFrame state
                # ✔ Wraps load in try/except
                # ✔ Prints only the shape
                # ✔ Handles missing file

    def clean(self):
       
        initial_rows = len(self.df) # Number of rows at the start.
        initial_missing = self.df.isna().sum().sum() # Number if missing values at the start.
        initial_dupes = self.df.duplicated(subset=["employee_id"]).sum() # Number of duplicate IDs at st the start.
        
        # Updates the DataFrame by modifying the object's internal state while keeping the data frame intact by cleaning individual columns in the table.
        self.df.drop_duplicates(subset=["employee_id"], keep="first") # Remove duplicate employee ID #'s; Keeps first occurence.
        
        self.df["name"] = self.df["name"].str.strip().str.title() # Standardizes employee Names.
        
        self.df["department"] = self.df["department"].str.strip().str.lower().map(self.DEPT_MAP) # Standardizes employee departments using mapping and domain knowledge.
        
        self.df["office_location"] = self.df["office_location"].str.strip().str.lower().map(self.LOC_MAP) # Standardizes employee office locations using mapping and domain knowledge.

    # Convert Types and Clean the Table
        def salary_helper(value): 
            '''Takes one salary value and returns a clean numeric salary or None.'''
            
            text = str(value) # Convert input to string for cleaning.
            
            text = text.strip() # Removes all whitespace.
            
            clean_value = re.sub(r'[$,]', '', text) # Regular expressopn to removes "$" and "," from the string. 
            
            if clean_value == "": return None # Return None if the string is empty after cleaning.
            
            try: clean_float = float(clean_value) # Error handling.
            except ValueError: return None
            
            if clean_float < 0: return None # Return None if salary is negative.
             
            return clean_float # Return cleaned, float salary value.
                    
        self.df["salary"].apply(salary_helper) # Cleans salary column value by value.         
        self.df["salary"] = self.df["salary"] = pd.to_numeric(self.df["salary"], errors="coerce")
        
        self.df["years_experience"] = pd.to_numeric(self.df["years_experience"], errors="coerce") # Every value in the column is set to numeric.
        self.df.loc[self.df["years_experience"] > 50, "years_experience"] = None # Selects and changes every row that meets the outlier condition.
        
        self.df["satisfaction_score"] = pd.to_numeric(self.df["satisfaction_score"], errors="coerce") # Every value in the column is set to numeric.
        self.df.loc[self.df["satisfaction_score"] < 1, "satisfaction_score"] = None # Outliers set to numbers outside 1-10.
        self.df.loc[self.df["satisfaction_score"] > 10, "satisfaction_score"] = None
        
        self.df["survey_date"] = pd.to_datetime(self.df["survey_date"], errors="coerce")
        
        def date_helper(value): # Helper that cleans one date value at a time.
            text = str(value) # Normalizes the input so I can safely manipulate it.
            clean_value = text.strip() # Removes whitspace for safe cleaning.
            
            formats = ["%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"] # List of formats that each value will cleanly loop through
            
            for fmt in formats: # Loop to try each format. 
                try:
                    return pd.to_datetime(clean_value, format=fmt) # Try one format and return value immediately if succesful. If it fails, tries the next one.
                except ValueError:                                 # Error handling.
                    continue
            return None
        
        self.df["survey_date"] = self.df["survey_date"].apply(date_helper) # Applies helper to the column.
        
        # Final State after cleaning.
        final_rows = len(self.df)
        final_missing = self.df.isna().sum().sum()
        
        # Calculate Differences.
        removed_dupes = initial_dupes
        new_missing = final_missing - initial_missing
        
        # Print Summary:
        print("\n=== Cleaning Summary ===")
        print(f"Removed duplicate employee IDs: {removed_dupes}")
        print(f"New missing values created during cleaning: {new_missing}")
        print(f"Rows before cleaning: {initial_rows}")
        print(f"Rows after cleaning:  {final_rows}")
        print("========================")
                
        return self # Returns self for chainability.
        

    def analyze(self):
        """Compute summary statistics from the cleaned self.df.

        Compute and print:

        4. Pearson correlation between years_experience and salary
           Hint: drop rows where either is NaN, then Series.corr()

        5. One additional insight of your choice (e.g., satisfaction by location)

        Return a dict with all results so main.py can use them.
        Keys to use: "avg_salary_by_dept", "avg_satisfaction_by_dept",
                     "headcount_by_location", "experience_salary_correlation",
                     "avg_satisfaction_by_location"
        """
        # Calculates and prints average salary.
        avg_salary = self.df.groupby("department")["salary"].mean().round(0)
        print("\nAverage salary by department:")
        print(avg_salary)
        
        #Calculates and prints average satisfaction score.
        avg_satisfaction = self.df.groupby("department")["satisfaction_score"].mean().round(0)
        print("\nAverage satisfaction score by department:")
        print(avg_satisfaction)
        
        #Calculates and prints employee headcount by location.
        emp_by_loc = self.df["office_location"].value_counts()
        print("\nEmployee Headcount by Location:")
        print(emp_by_loc)
        
        

    def visualize(self, output_path="output/charts.png"):
        """Create and save visualizations to `output_path`.

        Required charts:
        - Bar chart: average salary by department
        - Histogram: satisfaction score distribution (bins 1–10)
        Bonus:
        - Horizontal bar: headcount by office location

        Use matplotlib with plt.subplots() for a multi-chart layout.
        Save with plt.savefig(output_path, dpi=120, bbox_inches="tight").
        Call plt.close() after saving.

        Hint: import matplotlib; matplotlib.use("Agg") at top of file
              prevents errors when no display is available.

        Args:
            output_path: where to save the PNG file
        """
        # TODO: implement visualize()
        pass

    def export(self, output_path="output/clean_employees.csv"):
        """Save the cleaned self.df to a CSV at `output_path`.

        Create the output directory if it doesn't exist.
        Wrap in try/except.

        Hint: df.to_csv(output_path, index=False)

        Args:
            output_path: path for the exported CSV
        """
        # TODO: implement export()
        pass

    def run(self):
        """Execute the full pipeline: clean → analyze → visualize → export.

        Build output paths using os.path.join(os.path.dirname(__file__), "output", ...).
        Return the results dict from analyze().
        """
        # TODO: call each method in order and return results
        pass
    
DataPipeline("messy_employee_survey.csv").clean().analyze()