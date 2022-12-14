import React from "react";
import { Select } from "./components/Select";

function App({ choices, data, errors }) {
  return <Select choices={choices} data={data} errors={errors} />;
}

export default App;
