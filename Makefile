run:
	@python main.py

frmt:
	@python -m black $(shell find . -type f -name "*.py")
