import { Formik } from "formik";
import React, { useState } from "react";
import { Wizard } from "react-use-wizard";
import * as Yup from "yup";
import Debug from "./components/Debug";
import { Step1, Step2, Step3 } from "./components/steps";
import codelists from "./data/codelists.json";

function App() {
  const codelistTypes = codelists.map((a) => a.id);
  const [codelistCount, setCodelistCount] = useState(1);

  const FormSchema = Yup.lazy(() =>
    Yup.object().shape({
      codelistType0: Yup.string()
        .oneOf(codelistTypes)
        .required("Choose a codelist type"),
      codelist0: Yup.string().required("Select a codelist"),
      ...(codelistCount === 2
        ? {
            codelistType1: Yup.string()
              .oneOf(codelistTypes)
              .required("Choose a codelist type"),
            codelist1: Yup.string().required("Select a codelist"),
          }
        : {}),
    })
  );

  return (
    <>
      <Formik initialValues={{}} validationSchema={FormSchema} validateOnMount>
        <>
          <Wizard>
            <Step1
              codelistCount={codelistCount}
              setCodelistCount={setCodelistCount}
            />
            <Step2 />
            <Step3 />
          </Wizard>
          <Debug />
        </>
      </Formik>
    </>
  );
}

export default App;
