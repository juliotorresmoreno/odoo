package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path"

	"github.com/gorilla/mux"
)

var ignoreList = []string{"postgres", "template0", "template1"}

func HttpHandler() http.Handler {
	r := mux.NewRouter()

	r.HandleFunc("/backup", BackupHandler()).Methods("POST")
	r.PathPrefix("/backup/{dbname}").Handler(http.StripPrefix("/backup/", http.HandlerFunc(ScanBackupDirectory))).Methods("GET")
	r.PathPrefix("/download/{dbname}/{file}").Handler(http.StripPrefix("/download/", http.HandlerFunc(DownloadBackup))).Methods("GET")

	return r
}

func DownloadBackup(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	dbName := vars["dbname"]
	fileName := vars["file"]

	if dbName == "" || fileName == "" {
		http.Error(w, "Database name and file name are required", http.StatusBadRequest)
		return
	}

	outputDir := os.Getenv("ODOO_BACKUP_PATH")
	filePath := path.Join(outputDir, dbName, fileName)

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.Error(w, "Backup file not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	w.Header().Set("Content-Type", "application/octet-stream")
	http.ServeFile(w, r, filePath)
}

func ScanBackupDirectory(w http.ResponseWriter, r *http.Request) {
	OutputDir := os.Getenv("ODOO_BACKUP_PATH")
	dbName := mux.Vars(r)["dbname"]
	if dbName == "" {
		http.Error(w, "Database name is required", http.StatusBadRequest)
		return
	}

	paths, err := os.ReadDir(path.Join(OutputDir, dbName))
	if err != nil {
		http.Error(w, fmt.Sprintf("Error reading backup directory: %v", err), http.StatusInternalServerError)
		return
	}

	var backups []string
	for _, path := range paths {
		if !path.IsDir() && path.Name() != "README.md" {
			backups = append(backups, path.Name())
		}
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"files":  backups,
		"dbname": dbName,
		"output": OutputDir,
		"ignore": ignoreList,
	})
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
