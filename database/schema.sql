CREATE TABLE conversation (
    conversation_id SERIAL PRIMARY KEY,
    raw_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE structured_summary_raw (
    id SERIAL PRIMARY KEY,

    conversation_id INT NOT NULL
        REFERENCES conversation(conversation_id)
        ON DELETE CASCADE,

    transcript TEXT NOT NULL,
    summary_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE conversation_summary (
    summary_id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversation(conversation_id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position_title VARCHAR(255),
    start_date DATE,
    end_date DATE
);


CREATE TABLE patient (
    patient_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255),
    age INTEGER,
    sex VARCHAR(50),
    race_ethnicity VARCHAR(100),
    weight_lb NUMERIC,
    height_in NUMERIC,
    occupation VARCHAR(255)
);


CREATE TABLE visit (
    visit_id SERIAL PRIMARY KEY,
    visit_date DATE DEFAULT CURRENT_DATE,
    doctor_id INTEGER REFERENCES doctor(doctor_id),
    patient_id INTEGER REFERENCES patient(patient_id),
    visit_reason TEXT,
    conversation_id INTEGER REFERENCES conversation(conversation_id)
);


CREATE TABLE patient_medical_history (
    medical_history_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient(patient_id) ON DELETE CASCADE,
    physiological_context TEXT,
    psychological_context TEXT,
    vaccination_history TEXT,
    allergies TEXT,
    exercise_frequency TEXT,
    nutrition TEXT,
    sexual_history TEXT,
    alcohol_consumption TEXT,
    drug_usage TEXT,
    smoking_status TEXT,
    additional_details TEXT
);


CREATE TABLE surgeries (
    surgery_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient(patient_id) ON DELETE CASCADE,
    surgery_reason TEXT,
    surgery_type TEXT,
    procedure_datetime TIMESTAMPTZ,
    outcome TEXT,
    additional_details TEXT
);


CREATE TABLE symptoms (
    symptom_id SERIAL PRIMARY KEY,
    visit_id INTEGER REFERENCES visit(visit_id) ON DELETE CASCADE,
    symptom_name TEXT,
    intensity TEXT,
    location TEXT,
    duration TEXT,
    additional_details TEXT
);


CREATE TABLE treatments (
    treatment_id SERIAL PRIMARY KEY,
    visit_id INTEGER REFERENCES visit(visit_id) ON DELETE CASCADE,
    treatment_name TEXT,
    related_condition TEXT,
    dosage TEXT,
    duration TEXT,
    frequency TEXT,
    reason TEXT,
    reaction TEXT,
    additional_details TEXT
);




-- CREATE TABLE visits (
--     id INT PRIMARY KEY,
--     visit_motivation TEXT
-- );

-- CREATE TABLE admissions (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     reason VARCHAR(255),
--     date VARCHAR(100),
--     duration VARCHAR(100),
--     care_center_details TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );

-- CREATE TABLE patient_information (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     age VARCHAR(100),
--     sex VARCHAR(50),
--     ethnicity VARCHAR(100),
--     weight VARCHAR(50),
--     height VARCHAR(50),
--     family_medical_history TEXT,
--     recent_travels TEXT,
--     socio_economic_context TEXT,
--     occupation VARCHAR(255),
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );

-- CREATE TABLE patient_medical_history (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     physiological_context TEXT,
--     psychological_context TEXT,
--     vaccination_history TEXT,
--     allergies TEXT,
--     exercise_frequency TEXT,
--     nutrition TEXT,
--     sexual_history TEXT,
--     alcohol_consumption TEXT,
--     drug_usage TEXT,
--     smoking_status TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );

-- CREATE TABLE surgeries (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     reason TEXT,
--     type VARCHAR(255),
--     time VARCHAR(100),
--     outcome TEXT,
--     details TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );

-- CREATE TABLE symptoms (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     name_of_symptom TEXT,
--     intensity VARCHAR(100),
--     location VARCHAR(255),
--     time VARCHAR(100),
--     temporalisation VARCHAR(255),
--     behaviours_affecting TEXT,
--     details TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );

-- CREATE TABLE medical_examinations (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     name VARCHAR(255),
--     result TEXT,
--     details TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );

-- CREATE TABLE diagnosis_tests (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     test VARCHAR(255),
--     severity VARCHAR(100),
--     result TEXT,
--     condition_name VARCHAR(255),
--     time VARCHAR(100),
--     details TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );


-- CREATE TABLE treatments (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     name VARCHAR(255),
--     related_condition VARCHAR(255),
--     dosage VARCHAR(100),
--     time VARCHAR(100),
--     frequency VARCHAR(100),
--     duration VARCHAR(100),
--     reason_for_taking TEXT,
--     reaction_to_treatment TEXT,
--     details TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );

-- CREATE TABLE discharges (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     visit_id INT,
--     reason TEXT,
--     referral TEXT,
--     follow_up TEXT,
--     discharge_summary TEXT,
--     FOREIGN KEY (visit_id) REFERENCES visits(id)
-- );