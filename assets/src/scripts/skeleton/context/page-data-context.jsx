import * as React from "react";

const PageDataContext = React.createContext();

function pageDataReducer(state, action) {
  switch (action.type) {
    default: {
      throw new Error(`Unhandled action type: ${action.type}`);
    }
  }
}

function PageDataProvider({ children, data }) {
  const [state, dispatch] = React.useReducer(pageDataReducer, { data });
  const value = { state, dispatch };

  return (
    <PageDataContext.Provider value={value}>
      {children}
    </PageDataContext.Provider>
  );
}

function usePageData() {
  const context = React.useContext(PageDataContext);
  if (context === undefined) {
    throw new Error("usePageData must be used within a PageDataProvider");
  }
  return context;
}

export { PageDataProvider, usePageData };
