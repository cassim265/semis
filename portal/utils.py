def calculate_grade(percentage, class_name):
    """
    Converts percentage score to grade based on class level.
    """
    if percentage is None:
        return "-"

    score = float(percentage)
    class_lower = str(class_name).lower()

    # FORM 3 & FORM 4 GRADING (1 to 9 scale)
    if 'form 3' in class_lower or 'form 4' in class_lower:
        if score >= 90:
            return "1 (Distinction)"
        elif score >= 80:
            return "2 (Distinction)"
        elif score >= 70:
            return "3 (Strong Credit)"
        elif score >= 60:
            return "4 (Credit)"
        elif score >= 50:
            return "5 (Credit)"
        elif score >= 40:
            return "6 (Credit)"
        elif score >= 30:
            return "7 (Pass)"
        elif score >= 20:
            return "8 (Failed)"
        else:
            return "9 (Failed)"

    # FORM 1 & FORM 2 GRADING (A to F scale)
    else:
        if score >= 90:
            return "1 (A)"
        elif score >= 80:
            return "2 (A)"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        elif score >= 40:
            return "E"
        else:
            return "F"

