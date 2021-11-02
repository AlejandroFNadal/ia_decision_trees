import math
class SetCases:
    """Represents a set of cases to train with. Made as a class because many operations are based on a set of cases.
    """    
    def __init__(self,cases,case_count,class_column_name,classValues):
        """constructor

        Args:
            cases (Dataframe): cases
            case_count (int): amount of rows of dataframe
            class_column_name (str): name of class column
            classValues (list): possible values of class
        """        
        self.cases = cases
        self.classValues = classValues
        self.class_column_name = class_column_name
        self.case_count = case_count
        self.columns = list(cases.columns)
        self.attributes = [item for item in self.columns if item != self.class_column_name] # attributes, header without class
        
    def cases_count(self):        
        self.case_count = self.cases.shape[0]
        return self.case_count
        
    def get_attributes(self) -> list:
        return self.attributes
    
    def entropy(self) -> float: 
        """Entropy Formula function

        Returns:
            float: entropy for the whole set of cases
        """        
        entropy = 0
        for item in self.classValues:
            # get probability of occurrence for each class value
            prob = self.cases[self.cases[self.class_column_name]==item][self.class_column_name].count()/self.case_count
            # continue to next iteration because the probability is 0, thus, it is not present on current set
            if prob == 0:
                continue
            entropy -= (prob)*(math.log2(prob))
        return round(entropy,3)

    def entropy_attribute(self) -> dict: 
        """Entropy for each attribute

        Returns:
            dict: entropy for each attribute
        """        
        entropy_result = {}
        for attribute in self.attributes: 
            result = 0
            #possible values for that attributes
            attr_indexes = list(self.cases[attribute].value_counts().index)
            # paralel list containing amount of occurences for each possible values of attribute
            attr_counts = list(self.cases[attribute].value_counts().values)
            i=0
            for value in attr_indexes: # loop through each possible attribute value
                attr_entropy = 0
                attr_count = attr_counts[i]

                for c_value in self.classValues: # loop over every possible value for class
                    # number of occurences for each class value in the subset of cases that have a particular value of an attribute
                    class_count = len(self.cases[(self.cases[attribute]==value)&(self.cases[self.class_column_name]==c_value)])
                    # if class_count is zero, the attribute value and the class value did not appear together in any case of the subset
                    if class_count != 0:
                        #entropy for attribute value formula
                        attr_entropy -= (class_count/attr_count) * (math.log2((class_count/attr_count)))
                    else:
                        attr_entropy -= 0
                i+=1
                # entropy for attribute
                result += (attr_count/self.case_count) * attr_entropy 
            entropy_result[attribute] = result
        return entropy_result

    def gain2(self) -> list: 
        """Calculates gain for each attribute of a set

        Returns:
            list: return list of [Att, Value], something like: [[Att1, Value] [Att2, Value]]
        """         
        # first we require the values for entropy of set and entropy for each attribute
        entropy = self.entropy()
        entropy_atts = self.entropy_attribute()
        curr_gain = 0
        max_gain = 0
        result = []
        #loop through all keys in dictionary of entropy of attributes
        for key,value in entropy_atts.items():
            #get gain by substraction of entropy minus entropy of each atributes
            curr_gain = float(entropy) - value
            # the first element of the list will be the one with the biggest gain, the rest will be in any order
            if curr_gain > max_gain:
                result.insert(0, [key, curr_gain])
                max_gain=curr_gain
            else:
                result.append([key, curr_gain])      
        return result
    
    def gain_ratio(self) -> list:
        """calculates all gain ratio values for each attribute of a set

        Returns:
            list: [[attribute_name, gain_ratio_value]]
        """        
        # first we require the values for entropy and gain for each attribute
        entropy = self.entropy()
        gain = self.gain2()
        split_info = 0
        max_gain_rate = 0
        result=[0,0]
        #loop through all keys in dictionary of gain of attribute
        for att_name, gain_per_att in gain: # gain is [Att, Value]
            # We generate a list of all the quantities of occurences of each attribute
            attr_counts = list(self.cases[att_name].value_counts().values)
            split_info = 0
            for attr_count in attr_counts:
                # formula for split info
                split_info -= (attr_count/self.case_count) * (math.log2((attr_count/self.case_count)))
            # if any of the values are 0, the gain of the attribute is set to 0
            if ((split_info != 0.0) and (gain_per_att != 0.0)):
                curr_gain_rate = gain_per_att / split_info
            else:
                curr_gain_rate = 0
            # we return the attribute and value of gain ratio of the attribute with the biggest gain ratio
            if curr_gain_rate > max_gain_rate: 
                max_gain_rate = curr_gain_rate
                result[0] = att_name
                result[1] = curr_gain_rate
        return result

    def is_pure(self) -> bool:
        """Returns true if the set is pure, meaning that all cases have the same class value

        Returns:
            bool: if all cases have the same class value, returns True, otherwise False
        """
        #Get the amount of distinct values for the class column
        classes = self.cases[self.class_column_name].unique()
        if len(classes) == 1:
            return True
        return False
    
    def most_frequent_class(self) -> str:
        """Returns the most frequent class value in the set

        Returns:
            str: name of the most frequent class value
        """        
        #If more than one value has the same most frequent value, return the first one
        return self.cases[self.class_column_name].mode().tolist()[0]
    
    def separate_data(self, attr) -> list: # Esto retorna un arreglo con dataframes
        """Separates the cases in the set into subsets based on the value of an attribute
        Args:
            attr ([str]): name of the attribute to be used for separating the cases

        Returns:
            list: [DataFrame1,DataFrame2,...] array of dataframes, each one with the cases for one value of the attribute
        """        
        attr_values = list(self.cases[attr].unique())
        frames = []
        for val in attr_values:
            frames.append([val, self.cases[self.cases[attr]==val] ])
        return frames