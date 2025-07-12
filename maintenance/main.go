package main

import (
	"log"
	"net/http"
	"os"

	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
	"github.com/robfig/cron/v3"
)

func main() {
	if _, err := os.Stat(".env"); err == nil {
		if err := godotenv.Load(); err != nil {
			log.Fatal("Error loading .env file")
		}
	}

	c := cron.New()

	// Ejecutar a las 00:00 y 07:00
	c.AddFunc("0 0 * * *", func() {
		_, err := backupAllDatabases()
		if err != nil {
			log.Printf("Error in backupAllDatabases: %v", err)
		}
	})
	c.AddFunc("0 7 * * *", func() {
		_, err := backupAllDatabases()
		if err != nil {
			log.Printf("Error in backupAllDatabases: %v", err)
		}
	})
	c.Start()

	httpServer := http.Server{
		Addr:    ":8080",
		Handler: HttpHandler(),
	}

	log.Println(httpServer.ListenAndServe())
}
