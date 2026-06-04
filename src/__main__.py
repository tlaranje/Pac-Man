try:
  from src.visualizer import Manager
  from rich import print

  if __name__ == "__main__":
    manager = Manager()
    manager.run()
except Exception as e:
    print(e)
