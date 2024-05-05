import { RouterProvider } from "react-router-dom";
import PageRouter from "./lib/page-router";

export default function App() {
  return <RouterProvider router={PageRouter()} />;
}
