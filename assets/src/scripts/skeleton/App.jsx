import { Form, Formik } from "formik";
import React, { useState } from "react";
import { Wizard } from "react-use-wizard";
import * as Yup from "yup";
import Debug from "./components/Debug";
import { Step1, Step2, Step3, Step4, Step5 } from "./components/steps";
import codelists from "./data/codelists.json";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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
    <Formik
      initialValues={{}}
      onSubmit={async (values) => {
        await sleep(500);
        alert(JSON.stringify(values, null, 2));
      }}
      validateOnMount
      validationSchema={FormSchema}
    >
      <Form>
        <Wizard>
          <Step1
            codelistCount={codelistCount}
            setCodelistCount={setCodelistCount}
          />
          <Step2 codelistCount={codelistCount} />
          <Step3 />
          <Step4 />
          <Step5 />
        </Wizard>
        <Debug />
      </Form>
    </Formik>
  );
}

export default App;
