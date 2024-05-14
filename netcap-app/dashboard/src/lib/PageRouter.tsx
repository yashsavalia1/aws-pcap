import { createBrowserRouter } from "react-router-dom";
import NotFound from "../pages/404";

export default function PageRouter() {
  const pages = import.meta.glob("../pages/**/*.tsx", { eager: true });

  const routes = [];
  for (const path of Object.keys(pages)) {
    const fileName = path.match(/\.\/pages\/(.*)\.tsx$/)?.[1];

    if (!fileName) {
      continue;
    }

    const normalizedPathName = fileName.includes("$")
      ? fileName.replace("$", ":")
      : fileName.replace(/\/index/, "");

    routes.push({
      path: fileName === "index" ? "/" : `/${normalizedPathName.toLowerCase()}`,
      Element: (pages[path] as any).default,
      loader: (pages[path] as any)?.loader,
      action: (pages[path] as any)?.action,
      ErrorBoundary: NotFound,
    });
  }

  return createBrowserRouter(
    routes.map(({ Element, ErrorBoundary, ...rest }) => ({
      ...rest,
      element: <Element />,
      ...(ErrorBoundary && { errorElement: <ErrorBoundary /> }),
    }))
  );
}
