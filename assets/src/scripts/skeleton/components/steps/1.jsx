import { Form, Formik } from "formik";
import { default as React, useState } from "react";
import { useWizard } from "react-use-wizard";
import * as Yup from "yup";
import useFormData from "../../stores/form-data";
import codelists from "../../data/codelists.json";
import CodelistSelect from "../CodelistSelect";
import Button from "../Button";

function Step1() {
  const { nextStep } = useWizard();

  const formData = useFormData((state) => state.formData);
  const { replaceFormData } = useFormData();

  const [isSecondCodelistVisible, setIsSecondCodelistVisible] = useState(
    !!formData?.codelist2
  );

  const FormSchema = Yup.object().shape({
    codelistType1: Yup.string()
      .oneOf(["event", "medication"])
      .required("Choose a codelist type"),
    codelist1: Yup.object().shape({
      label: Yup.string().required(),
      organisation: Yup.string().required(),
      value: Yup.string().required(),
    }),
    codelistType2: isSecondCodelistVisible
      ? Yup.string().oneOf(["event", "medication"]).required("Required")
      : undefined,
    codelist2: isSecondCodelistVisible
      ? Yup.object().shape({
          label: Yup.string().required(),
          organisation: Yup.string().required(),
          value: Yup.string().required(),
        })
      : undefined,
  });

  return (
    <div>
      <Formik
        initialValues={{
          codelist1: formData?.codelist1,
          codelistType1: formData?.codelistType1,
          codelist2: formData?.codelist2,
          codelistType2: formData?.codelistType2,
        }}
        validationSchema={FormSchema}
        onSubmit={(values) => {
          replaceFormData(values);
          nextStep();
        }}
        validateOnMount
      >
        {({
          errors,
          touched,
          values,
          setFieldValue,
          isValid,
          validateForm,
          validateField,
        }) => {
          return (
            <Form>
              <CodelistSelect
                codelists={codelists}
                errors={errors}
                setFieldValue={setFieldValue}
                touched={touched}
                values={values}
                id={1}
              />
              <div className="my-8 flex flex-row gap-6">
                {!isSecondCodelistVisible ? (
                  <Button
                    variant="success"
                    type="button"
                    onClick={() => setIsSecondCodelistVisible(true)}
                  >
                    Add another codelist
                  </Button>
                ) : null}
              </div>
              {isSecondCodelistVisible ? (
                <CodelistSelect
                  codelists={codelists}
                  errors={errors}
                  setFieldValue={setFieldValue}
                  touched={touched}
                  values={values}
                  id={2}
                />
              ) : null}
              {isSecondCodelistVisible ? (
                <Button
                  variant="danger"
                  type="button"
                  onClick={() => {
                    setIsSecondCodelistVisible(false);
                    setFieldValue("codelist2", undefined);
                    setFieldValue("codelistType2", undefined);
                    validateForm();
                    validateField("codelist2");
                    validateField("codelistType2");
                  }}
                >
                  Remove this codelist
                </Button>
              ) : null}
              <div className="block my-3">
                <Button
                  disabled={!isValid}
                  variant="primary"
                  size="lg"
                  type="submit"
                >
                  Next
                </Button>
              </div>
              <div className="my-8 p-8 bg-blue-50 overflow-x-scroll">
                <pre>{JSON.stringify(values, null, 2)}</pre>
              </div>
            </Form>
          );
        }}
      </Formik>
    </div>
  );
}

export default Step1;
