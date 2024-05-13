import { RouterProvider } from "react-router-dom";
import PageRouter from "./lib/PageRouter";

export default function App() {
  return <RouterProvider router={PageRouter()} />;
}
