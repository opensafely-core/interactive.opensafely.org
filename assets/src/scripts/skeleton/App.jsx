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
      codelist0: Yup.object().shape({
        label: Yup.string().required(),
        organisation: Yup.string().required(),
        value: Yup.string().required(),
      }),
      ...(codelistCount === 2
        ? {
            codelistType1: Yup.string()
              .oneOf(codelistTypes)
              .required("Choose a codelist type"),
            codelist1: Yup.object().shape({
              label: Yup.string().required(),
              organisation: Yup.string().required(),
              value: Yup.string().required(),
            }),
          }
        : {}),
      frequency: Yup.string()
        .oneOf(["monthly", "quarterly", "yearly"])
        .required("Select a frequency"),
    })
  );

  return (
    <Formik initialValues={{}} validateOnMount validationSchema={FormSchema}>
      <>
        <Wizard>
          <Step1
            codelistCount={codelistCount}
            setCodelistCount={setCodelistCount}
          />
          <Step2 codelistCount={codelistCount} />
          <Step3 />
        </Wizard>
        <Debug />
      </>
    </Formik>
  );
}

export default App;
