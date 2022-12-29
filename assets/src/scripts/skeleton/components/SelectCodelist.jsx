import { useFormikContext } from "formik";
import { number, string } from "prop-types";
import React, { Fragment } from "react";
import { usePageData } from "../context/page-data-context";
import codelists from "../data/codelists.json";
import { classNames } from "../utils";
import Combobox from "./Combobox";
import RadioButton from "./RadioButton";

function SelectCodelist({ label, id }) {
  const codelist = `codelist${id}`;
  const codelistType = `codelistType${id}`;
  const codelistGroup = `codelistGroup${id}`;

  const {
    state: { data },
  } = usePageData();
  const {
    errors,
    setFieldError,
    setFieldTouched,
    setFieldValue,
    touched,
    validateForm,
    values,
  } = useFormikContext();

  const radioButtonChange = (item) => {
    if (item.id !== values[codelistType]) {
      setFieldValue(codelist, "");
      setFieldTouched(codelist, false);
    }
  };

  const handleSelectedItemChange = (item) => {
    setFieldError(codelist, undefined);
    setFieldValue(codelist, item?.selectedItem || undefined);
    setFieldTouched(codelist, true);
    setTimeout(() => validateForm(), 0);
  };

  return (
    <>
      <fieldset className={classNames(id > 0 ? "mt-10" : null)}>
        <legend className="text-4xl font-bold mb-4">
          <h2 className="">{label} type</h2>
        </legend>
        <div className="flex flex-row gap-9">
          {codelists.map((item) => (
            <RadioButton
              key={`${codelistType}_${item.id}`}
              id={`${codelistType}_${item.id}`}
              label={item.name}
              name={codelistType}
              onClick={() => radioButtonChange(item)}
              value={item.id}
            />
          ))}
          {errors[codelistType] && touched[codelistType] ? (
            <div>{errors[codelistType]}</div>
          ) : null}
        </div>
      </fieldset>
      <div aria-labelledby={codelistGroup} className="w-full mt-6" role="group">
        {codelists.map((item) => (
          <Fragment key={item.id}>
            {item.id === values[codelistType] ? (
              <>
                <Combobox
                  choices={data}
                  data={{
                    choices: "",
                    errors: "",
                    hint: "",
                    id: "",
                    label,
                    name: "",
                  }}
                  errors={[""]}
                  handleSelectedItemChange={(i) => handleSelectedItemChange(i)}
                  initialSelectedItem={values[codelist] || null}
                />
                {errors[codelist] && touched[codelist] ? (
                  // eslint-disable-next-line no-console
                  <div>{console.log(errors[codelist])}</div>
                ) : null}
              </>
            ) : null}
          </Fragment>
        ))}
      </div>
    </>
  );
}

export default SelectCodelist;

SelectCodelist.propTypes = {
  label: string.isRequired,
  id: number.isRequired,
};
