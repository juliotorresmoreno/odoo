package main

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
)

var ignoreList = []string{"postgres", "template0", "template1"}

func HttpHandler() http.Handler {
	r := mux.NewRouter()

	r.HandleFunc("/backup", BackupHandler()).Methods("POST")

	return r
}

func BackupHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		backups, err := backupAllDatabases()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(backups)
	}
}
