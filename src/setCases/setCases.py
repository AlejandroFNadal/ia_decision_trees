import math
class SetCases:
    def __init__(self,cases,case_count,class_column_name,classValues):
        self.cases = cases
        self.classValues = classValues
        self.class_column_name = class_column_name
        self.case_count = case_count
        self.columns = list(cases.columns)
        #self.attributes = self.columns
        self.attributes = [item for item in self.columns if item != self.class_column_name] # This is 'A' in the theory
        #self.attributes.remove(self.class_column_name)  
    def cases_count(self):
        self.case_count = self.cases.shape[0]
        return self.case_count
        
    def get_attributes(self) -> list:
        return self.attributes
    
    def entropy(self) -> float:  # Entropy Formula function
        entropy = 0
        counts = self.cases[self.class_column_name].value_counts()
        #print(f'counts {counts}')
        for item in self.classValues:
            prob = self.cases[self.cases[self.class_column_name]==item][self.class_column_name].count()/self.case_count
            #print(f'prob {prob}')
            #No se suma porque el conjunto actual no posee casos pertenecientes a uno de los valores de la clase
            if prob == 0:
                continue
            entropy -= (prob)*(math.log2(prob))
        return round(entropy,3)

    def entropy_attribute(self) -> float: # Entropia de cada tributo de 'A'
        entropy_result = {}
        for attribute in self.attributes:  # Bucle sobre cada atributo de la lista
            result = 0
            attr_indexes = list(self.cases[attribute].value_counts().index)
            attr_counts = list(self.cases[attribute].value_counts().values)
            i=0
            for value in attr_indexes: # Bucle sobre los valores posibles de cada atributo
                attr_entropy = 0
                attr_count = attr_counts[i]

                for c_value in self.classValues: # Bucle sobre cada caso de un valor posible de un atributo
                    class_count = len(self.cases[(self.cases[attribute]==value)&(self.cases[self.class_column_name]==c_value)])
                    if class_count != 0:
                        attr_entropy -= (class_count/attr_count) * (math.log2((class_count/attr_count)))
                    else:
                        attr_entropy -= 0 #ESTO SE TENDRIA QUE SACAR DE ACA, CUANDO ESTE EL CODIGO COMPLETO ESTO IRIA AL PRINCIPIO
                i+=1

                result += (attr_count/self.case_count) * attr_entropy # Resultado de entropia de un atributo posible
            entropy_result[attribute] = result
        return entropy_result

    def gain(self) -> list: # return [Att, Value]
        entropy = self.entropy()
        entropy_atts = self.entropy_attribute()
        max_gain = 0
        curr_gain = 0
        result = [0,0]
        for key,value in entropy_atts.items():
            curr_gain = float(entropy) - value 
            if curr_gain > max_gain:
                max_gain = curr_gain
                result[0] = key
                result[1] = curr_gain
        return result

    def gain2(self) -> list: # return list of [Att, Value], something like: [[Att1, Value] [Att2, Value]] 
        entropy = self.entropy()
        entropy_atts = self.entropy_attribute()
        curr_gain = 0
        max_gain = 0
        result = []
        #print(f'Entropia de la clase {entropy}')
        for key,value in entropy_atts.items():
            #print(f'Entropia del atributo {key} es {value}')
            curr_gain = float(entropy) - value
            if curr_gain > max_gain:
                result.insert(0, [key, curr_gain])
                max_gain=curr_gain
            else:
                result.append([key, curr_gain])      
        return result
    
    def gain_ratio(self) -> list:
        entropy = self.entropy()
        gain = self.gain2()
        split_info = 0
        max_gain_rate = 0
        result=[0,0]
        for att_name, gain_per_att in gain: # gain is [Att, Value]
            # We generate a list of all the quantities of occurences of each attribute
            attr_counts = list(self.cases[att_name].value_counts().values) # 
            split_info = 0
            for attr_count in attr_counts:
                split_info -= (attr_count/self.case_count) * (math.log2((attr_count/self.case_count)))
            if ((split_info != 0.0) and (gain_per_att != 0.0)):
                curr_gain_rate = gain_per_att / split_info
            else:
                curr_gain_rate = 0
            if curr_gain_rate > max_gain_rate: 
                max_gain_rate = curr_gain_rate
                result[0] = att_name
                result[1] = curr_gain_rate
        return result

    def is_pure(self) -> bool:
        classes = self.cases[self.class_column_name].unique()
        if len(classes) == 1:
            return True
        return False
    
    def most_frequent_class(self) -> str:
        #print(f'self.class_column_name {self.class_column_name}')
        return self.cases[self.class_column_name].mode().tolist()[0]
    
    def separate_data(self, attr) -> list: # Esto retorna un arreglo con dataframes
        attr_values = list(self.cases[attr].unique())
        frames = []
        for val in attr_values:
            frames.append([val, self.cases[self.cases[attr]==val] ])
        return frames