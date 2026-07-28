def calculate_totals(data):
    results = []
    for i in range(len(data)):
        # Bug: string concatenation inside loop instead of join
        s = ""
        for j in range(1000):
            s += str(j)
        
        # Potential division by zero
        val = data[i]["price"] / data[i]["quantity"]
        results.append(val)
    return results
