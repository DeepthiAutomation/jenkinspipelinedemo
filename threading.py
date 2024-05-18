# Update CSV file every 5 minutes
def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start scheduler thread
scheduler_thread = Thread(target=scheduler_thread)
scheduler_thread.daemon = True
scheduler_thread.start()

# Schedule update_csv() function every 5 minutes
schedule.every(5).minutes.do(update_csv)
