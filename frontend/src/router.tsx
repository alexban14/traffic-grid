import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  redirect,
} from "@tanstack/react-router";
import { Layout } from "./components/Layout";
import { LoginPage } from "./components/LoginPage";
import { Dashboard } from "./components/Dashboard";
import { TasksPage } from "./components/TasksPage";
import { IdentitiesPage } from "./components/IdentitiesPage";
import { WorkersPage } from "./components/WorkersPage";

const TOKEN_KEY = "trafficgrid_token";

function isAuthenticated(): boolean {
  return localStorage.getItem(TOKEN_KEY) !== null;
}

// Root route — just renders Outlet, no layout wrapper here
const rootRoute = createRootRoute({
  component: () => <Outlet />,
});

// Public login route
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/login",
  beforeLoad: () => {
    if (isAuthenticated()) {
      throw redirect({ to: "/" });
    }
  },
  component: LoginPage,
});

// Protected layout route — wraps all authenticated pages
const protectedRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: "protected",
  beforeLoad: () => {
    if (!isAuthenticated()) {
      throw redirect({ to: "/login" });
    }
  },
  component: () => (
    <Layout>
      <Outlet />
    </Layout>
  ),
});

const indexRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: "/",
  component: Dashboard,
});

const tasksRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: "/tasks",
  component: TasksPage,
});

const identitiesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: "/identities",
  component: IdentitiesPage,
});

const workersRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: "/workers",
  component: WorkersPage,
});

const routeTree = rootRoute.addChildren([
  loginRoute,
  protectedRoute.addChildren([indexRoute, tasksRoute, identitiesRoute, workersRoute]),
]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
