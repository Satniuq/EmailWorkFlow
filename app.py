while True:
    new_emails = email_gateway.fetch()
    for email in new_emails:
        ingestion.ingest(email)

    maintenance.run()
    sleep(30)
