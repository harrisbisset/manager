package api

import (
	"log/slog"

	"github.com/labstack/echo"
)

type API struct {
	port   int
	domain string

	App    *echo.Echo
	logger *slog.Logger
	// db     *sql.DB
}

func New(
	port int,
	domain string,
	app *echo.Echo,
	logger *slog.Logger,
	// db *mysql.Config,
) *API {
	echo := echo.New()

	echo.Static("/dist", "dist")
	echo.Static("/public", "public")

	api := &API{
		port:   port,
		domain: domain,
		App:    echo,
		logger: logger,
		// db:     data.GetConnection(db),
	}

	return api
}

func (a *API) GetApp() *echo.Echo {
	return a.App
}
