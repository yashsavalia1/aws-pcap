package dashboard

import (
	"fmt"
	"log"
	"net/url"
	"os"
	"os/exec"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

/* var (
	//go:embed dist/*
	dist embed.FS

	//go:embed dist/index.html
	indexHTML embed.FS

	distDirFS     = echo.MustSubFS(dist, "dist")
	distIndexHTML = echo.MustSubFS(indexHTML, "dist")
) */

func RegisterHandlers(e *echo.Echo) {
	if len(os.Args) > 1 && os.Args[1] == "--prod" {
		e.Use(middleware.StaticWithConfig(middleware.StaticConfig{
			Root:   "dashboard/dist",
			Browse: true,
			HTML5:  true,
		}))
	} else {
		fmt.Println("Running in dev mode")
		setupDevProxy(e)
	}
}

func setupDevProxy(e *echo.Echo) {
	// start the vite dev server
	cmd := exec.Command("npm", "run", "dev")
	cmd.Dir = "dashboard"
	err := cmd.Start()
	if err != nil {
		log.Fatal(err)
	}

	url, err := url.Parse("http://localhost:5173")
	if err != nil {
		log.Fatal(err)
	}
	// Setep a proxy to the vite dev server on localhost:5173
	balancer := middleware.NewRoundRobinBalancer([]*middleware.ProxyTarget{
		{
			URL: url,
		},
	})
	e.Use(middleware.ProxyWithConfig(middleware.ProxyConfig{
		Balancer: balancer,
		Skipper: func(c echo.Context) bool {
			// Skip the proxy if the prefix is /api
			return len(c.Path()) >= 4 && c.Path()[:4] == "/api"
		},
	}))
}
