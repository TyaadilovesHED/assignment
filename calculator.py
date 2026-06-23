#!/usr/bin/env python3
"""
Basic arithmetic calculator CLI
Supports: addition, subtraction, multiplication, division
"""

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Cannot divide by zero"
    return x / y

def calculator():
    print("=" * 40)
    print("     BASIC ARITHMETIC CALCULATOR")
    print("=" * 40)
    print("\nOperations:")
    print("  + : Addition")
    print("  - : Subtraction")
    print("  * : Multiplication")
    print("  / : Division")
    print("  q : Quit")
    print("=" * 40)
    
    while True:
        try:
            print("\nEnter calculation (e.g., '5 + 3'):")
            user_input = input("> ").strip()
            
            if user_input.lower() == 'q':
                print("Goodbye!")
                break
            
            parts = user_input.split()
            
            if len(parts) != 3:
                print("Error: Please use format 'number operator number' (e.g., '10 + 5')")
                continue
            
            num1_str, operator, num2_str = parts
            
            try:
                num1 = float(num1_str)
                num2 = float(num2_str)
            except ValueError:
                print("Error: Please enter valid numbers")
                continue
            
            if operator == '+':
                result = add(num1, num2)
            elif operator == '-':
                result = subtract(num1, num2)
            elif operator == '*':
                result = multiply(num1, num2)
            elif operator == '/':
                result = divide(num1, num2)
            else:
                print("Error: Invalid operator. Use +, -, *, or /")
                continue
            
            if isinstance(result, str):
                print(result)
            else:
                print(f"Result: {result}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    calculator()
