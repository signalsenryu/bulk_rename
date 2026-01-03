def test_setattr_explained(monkeypatch):
    # До подмены
    print(f"До: {input}")
    
    # Подмена
    monkeypatch.setattr("builtins.input", lambda prompt: f"fake: {prompt}")
    
    # После подмены
    print(f"После: {input}")
    result = input("Введи что-то: ")
    print(f"Result: {result}")