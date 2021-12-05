def main():
    import bjoern
 
    from fjfnaranjobot.wsgi import application
 

    bjoern.listen(application, "0.0.0.0", 8001)
    bjoern.run()

if __name__ == "__main__":
    main()
