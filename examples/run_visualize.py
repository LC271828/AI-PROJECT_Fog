def main():
	"""Launch the interactive visualizer menu (GUI).

	If pygame is not installed or initialization fails, print a helpful
	message and exit with a non-zero status.
	"""
	try:
		from src.visualize import run_menu  # lazy import to avoid hard dependency
	except Exception as e:
		print("Error: Unable to import GUI visualizer.\n"
		      "Hint: Install pygame via: powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1 -WithGUI",
		      flush=True)
		raise SystemExit(1)

	# Launch the interactive menu which will run the visualizer when selections are made.
	run_menu()


if __name__ == '__main__':
	main()
