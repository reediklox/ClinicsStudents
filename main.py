from ExcelParse.ParserDefault import Parser
from Location.location import Location, LocationNotFoundError
from ORMwork.SQLWriter import Writer
import json



def ValidateCoordinates(item):
    try:
        coordinates = Location(item)
        return coordinates
    except LocationNotFoundError as e:
        print(e)
        return
    

def ClinicCoordinates(clinics:dict) -> dict:
    coordinates = {}
    for clinic_name, clinic_addr in clinics.items():
        clinic_coordinates = ValidateCoordinates(clinic_addr)
        
        if not clinic_coordinates: continue
        coordinates[clinic_name] = clinic_coordinates
    return coordinates
        
        
def ReCreation(student_name:str, student_address:str, student_nation:str, clinics:dict) -> dict:
    student_coordinates = ValidateCoordinates(student_address)
    
    if not student_coordinates: return
    
    clinics_distanses = []    
    for clinic_name, clinic_coordinates in clinics.items():
        clinics_distanses.append((clinic_name, clinic_coordinates.DistanceDifference(student_coordinates)))    
    
    clinics_distanses.sort(key=lambda item: item[1])
    return {student_name: [clinics_distanses, student_nation]}


def GetNationality(students:list, students_dict:dict) -> list:
    result = []
    for student in students:
        result.append(students_dict[student][1])
    
    return result


def SearchFreePlace(final_dict:dict, clinic_name:str, nation:list, students:dict, nation_class:str):
    removed_student = final_dict[clinic_name].pop(nation.index(nation_class))
    for search_name in students[removed_student][0]:
        if search_name[0] == clinic_name or final_dict[clinic_name] is None:
            continue
        search_nation = GetNationality(final_dict[search_name[0]], students)
        if search_nation.count(nation_class) and len(final_dict[search_name[0]]) < 5:
            final_dict[search_name[0]].append(removed_student)
            break


def Correction(students:dict, final_dict:dict,):
    for clinic_name, student_list in final_dict.items():
        if final_dict[clinic_name] is None:
            continue
        nation = GetNationality(student_list, students)
        if nation.count('f') == 1:
            SearchFreePlace(final_dict, clinic_name, nation, students, 'f')
        if nation.count('c') == 1:
            SearchFreePlace(final_dict, clinic_name, nation, students, 'c')
                

def Direction(students:dict, clinics:list, student_clinic:dict, directed_students:list):
    student_copy = students.copy()
    
    redirect_later = {}
    for clinic in clinics:
        student_accessed = []
        for student_name, student_info in student_copy.items():
            if student_name in directed_students:
                continue
            if student_info[0][0][0] == clinic:
                try:
                    student_clinic_len = len(student_clinic[clinic])
                except TypeError:
                    student_clinic_len = 0
                
                if len(student_accessed) == 5 or (student_clinic_len + len(student_accessed) == 5):
                    for students_copy_name, students_copy_info in student_copy.items():
                        if students_copy_info[0][0][0] == clinic and students_copy_name not in directed_students:
                            student_copy[students_copy_name][0].pop(0)
                            redirect_later[students_copy_name] = students_copy_info
                    break
                
                student_accessed.append(student_name)
                directed_students.append(student_name)
            
        if len(student_accessed) != 0:
            if student_clinic[clinic]:
                student_clinic[clinic] = student_clinic[clinic] + student_accessed
            else:
                student_clinic[clinic] = student_accessed
    
    return student_clinic, redirect_later
                

def MainActivity(poly:dict, students:dict) -> dict:
    # with open('data_of_distance.json', 'r') as r:
    #     students_advanced = json.load(r)
    students_advanced = {}
    clinic_coordinates = ClinicCoordinates(poly)
    for student_name, student_info in students.items():
        row = ReCreation(student_name, student_info[0], student_info[1], clinic_coordinates)
        students_advanced.update(row)
    
    directed_students = []
    clinics_names = list(poly.keys())
    student_clinic = {k:[] for k in clinics_names}

    final_clinic_dict, redirect = Direction(students_advanced, clinics_names, student_clinic, directed_students)
    
    while redirect:
        final_clinic_dict, redirect = Direction(redirect, clinics_names, final_clinic_dict, directed_students)

    Correction(students_advanced, final_clinic_dict)
    
    return final_clinic_dict
    

def SetNation(dictionary, nation):
    for k, v in dictionary.items():
        dictionary[k] = [v, nation]


if __name__ == '__main__':
    headers = {'coutrymans': 1,
           'foreigners': 0,
           'polyclinics': 0}

    skiprows = {'coutrymans': 3,
                'foreiners': None,
                'polyclinics': None}

    Col = {'coutrymans': ['ФИО', 'Прописан:'],
                'foreiners': ['ФИО', 'Проживает'],
                'polyclinics': ['Название', 'Адрес']}
    
    Nationality = ['c', 'f']
    
    poly = Parser('resources/Polyclinics.xlsx', header=headers['polyclinics'], skiprows=skiprows['polyclinics'])
    coutrymans = Parser('resources/Students.xlsx', header=headers['coutrymans'], skiprows=skiprows['coutrymans'])
    foreigners = Parser('resources/Foreigners.xlsx', header=headers['foreigners'], skiprows=skiprows['foreiners'])
    
    polyDict = poly.getDict(Col['polyclinics'][0], Col['polyclinics'][1])
    
    coutrymansDict = coutrymans.getDict(Col['coutrymans'][0], Col['coutrymans'][1])
    SetNation(coutrymansDict, Nationality[0])
    
    foreignersDict = foreigners.getDict(Col['foreiners'][0], Col['foreiners'][1])
    SetNation(foreignersDict, Nationality[1])
    
    coutrymansDict.update(foreignersDict)
    
    with Writer('Final.db') as w:  
        final_dict = MainActivity(poly=polyDict, students=coutrymansDict)
        for clinic_name, students in final_dict.items():
            if students:
                w.isert(clinic_name, *students)
            else:
                w.isert(clinic_name)
        
        w.convertToExcel()