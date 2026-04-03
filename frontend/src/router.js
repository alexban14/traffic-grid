import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { createRootRoute, createRoute, createRouter, Outlet } from '@tanstack/react-router';
import { Dashboard } from './components/Dashboard';
const rootRoute = createRootRoute({
    component: () => (_jsx(_Fragment, { children: _jsx(Outlet, {}) })),
});
const indexRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/',
    component: Dashboard,
});
const routeTree = rootRoute.addChildren([indexRoute]);
export const router = createRouter({ routeTree });
//# sourceMappingURL=router.js.map