package handler

import (
	"github.com/harrisbisset/manager/views/index"
	"github.com/labstack/echo"
)

type IndexService interface {
}

type IndexHandler struct {
	IndexService IndexService
}

func (i IndexHandler) View(c echo.Context) error {
	return Render(c, index.Index())
}
