import pandas as pd
import matplotlib.pyplot as plt
import re
import matplotlib
import matplotlib.pyplot as plt
import os


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
        Print how many rows and columns were loaded."""
        
        self.filepath = filepath # Foundation of the object's state: storing the string filepath that the user entered.
        self.df = None # The DataFrame must live on the object so that all other methods can use it when called (shared state).
        
        # Load the CSV
        try:
            self.df = pd.read_csv(filepath) # Attempt to load the CSV; if successful, df becomes the DataFrame of the user provided filepath.
            print(self.df.shape) # (rows, columns) 
           
        except FileNotFoundError:
            print("File not found. Sorry for the inconvenience. Please try again.") # Error Handling with Grace.


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
        """Compute summary statistics from the cleaned self.df."""
        
        # Calculates and prints average salary by department.
        avg_salary = self.df.groupby("department")["salary"].mean().round(0)
        print("\nAverage salary by department:")
        print(avg_salary)
        
        # Calculates and prints average satisfaction score by department.
        avg_satisfaction = self.df.groupby("department")["satisfaction_score"].mean().round(0)
        print("\nAverage satisfaction score by department:")
        print(avg_satisfaction)
        
        # Calculates and prints employee headcount by location.
        employees_by_loc = self.df["office_location"].value_counts()
        print("\nEmployee Headcount by Location:")
        print(employees_by_loc)
        
        # Pearson Correlation: calcualtes and prints years of expereince and salary corr.
        subset = self.df[["years_experience", "salary"]].dropna()
        corr = subset["years_experience"].corr(subset["salary"])
        print(f"\nPearson correlation (years_experience vs salary): {corr:3f}")
        
        # Calculates and prints satisfaction by location.
        satisfaction_by_location = self.df.groupby("office_location")["satisfaction_score"].mean().round(0)
        print("\nAverage satisfaction score by office location:")
        print(satisfaction_by_location)
        
        # Dictionary of results that main.py can access
        return {
            "avg_salary_by_dept": avg_salary,
            "avg_satisfaction_by_dept": avg_satisfaction,
            "headcount_by_location": employees_by_loc,
            "experience_salary_correlation": corr,
            "avg_satisfaction_by_location": satisfaction_by_location
            }

        
    def visualize(self, results, output_path="output/charts.png"):
        matplotlib.use("Agg")   # prevents display errors
        """Create and save visualizations to `output_path.`"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5)) # One figure with 3 plots (1 row, 3 columns of plots).
        ax1, ax2, ax3 = axes # Names each axis.
        
        #Bar Chart: Average salary by department.
        avg_salary = results["avg_salary_by_dept"] # Grab Series from analyze().
        ax1.bar(avg_salary.index, avg_salary.values) # Make the bar chart. x-axis, y-axis.
        ax1.set_title("Average Salary by Department") # Title.
        ax1.set_xticklabels(axis="x", rotation=45) # No overlap.
        
        # Histogram for satisfaction distribution.
        ax2.hist(self.df["satisfaction_score"].dropna(), bins=10) # Make a histogram with 10 buckets.
        ax2.set_title("Satisfaction Distribution") # Title.
        
        # Horizontal bar chart: headcount by office location.
        headcount = results["headcount_by_location"] # Uses computed results from analyze().
        ax3.bar(headcount.index, headcount.values) # Makes horizontal bar chart.
        ax3.set_title("Headcount by Location") # Title.
        
        plt.tight_layout() # Auto-adjust spacing so labels don't overlap

        os.makedirs(os.path.dirname(output_path), exist_ok=True) # Debugging "FileNotFoundError" - Python now creates the folder automatically.
        plt.savefig(output_path, dpi=120, bbox_inches="tight") # Save the whole figure to a PNG file.
        
        plt.close() # Close figure.

    def export(self, output_path="output/clean_employees.csv"):
        """Save the cleaned self.df to a CSV at `output_path.`"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True) # Debugging "FileNotFoundError" - Python now creates
        self.df.to_csv(output_path, index=False)

    def run(self):
        """Execute the full pipeline: clean → analyze → visualize → export."""
        # Call each method in order and return results.
        #1. Clean the data.
        self.clean()    
        
        #2. Analyze the data.
        results = self.analyze()
        
        #3. Build absolute output paths.
        base_dir = os.path.dirname(__file__) # Folder where this .py file lives.
        output_dir = os.path.join(base_dir, "output") # /.../data-pipeline/output
        
        charts_path = os.path.join(output_dir, "charts.png") # Builds full path to chart image. 
        export_path = os.path.join(base_dir, "clean_employees.csv") # Builds the full path to cleaned CSV.
        
        #4. Visualize using the results dictionary.
        self.visualize(results, output_path=charts_path) # Uses results dict and saves chart to the correct absolute path.
        
        #5. Export cleaned data.
        self.export(output_path=export_path) #Saves the CSV to the correct absolute path.
        
        #6. Return the results dictionary.
        return results # Gives main.py access to print or use analysis.
    
 
    
pipeline = DataPipeline("messy_employee_survey.csv")
results = pipeline.run()
print(results)
