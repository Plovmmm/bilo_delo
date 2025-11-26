--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: marks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marks (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    visit_date date NOT NULL,
    address text,
    lat numeric(10,8) NOT NULL,
    lon numeric(11,8) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_coordinates CHECK ((((lat >= ('-90'::integer)::numeric) AND (lat <= (90)::numeric)) AND ((lon >= ('-180'::integer)::numeric) AND (lon <= (180)::numeric))))
);


ALTER TABLE public.marks OWNER TO postgres;

--
-- Name: marks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.marks_id_seq OWNER TO postgres;

--
-- Name: marks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marks_id_seq OWNED BY public.marks.id;


--
-- Name: photos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.photos (
    id integer NOT NULL,
    mark_id integer NOT NULL,
    filename character varying(255) NOT NULL,
    is_main boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.photos OWNER TO postgres;

--
-- Name: photos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.photos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.photos_id_seq OWNER TO postgres;

--
-- Name: photos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.photos_id_seq OWNED BY public.photos.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: marks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks ALTER COLUMN id SET DEFAULT nextval('public.marks_id_seq'::regclass);


--
-- Name: photos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photos ALTER COLUMN id SET DEFAULT nextval('public.photos_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: marks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marks (id, user_id, title, description, visit_date, address, lat, lon, created_at) FROM stdin;
3	2	Ногти	Ааааа\r\nНогти\r\n	2025-09-18	Санкт-Петербург, 8-я Советская улица, 44	59.93532484	30.37856506	2025-09-29 03:59:35.354505
4	2	Лавка		2025-09-27	Санкт-Петербург, улица Оптиков, 30	59.99906030	30.22044735	2025-09-29 04:06:51.463892
5	2	алексей аня и олег	на одном фото все!!!!!	2025-09-18	Санкт-Петербург, Елагин остров	59.97913585	30.26406538	2025-09-29 04:11:52.284349
7	1	asdsa	dasdsadas	2025-09-29	Санкт-Петербург, набережная Крюкова канала	59.92672584	30.29416351	2025-09-29 05:37:57.707369
9	2	лэти	кпувкепцып	2025-09-29	Санкт-Петербург, улица Профессора Попова, 5Д	59.97195507	30.32231749	2025-09-29 05:42:34.723504
10	1	asdasd		2025-09-29	Санкт-Петербург, набережная Обводного канала, 121Б	59.91121227	30.32471924	2025-09-29 05:56:29.667832
11	1	очтчтты		2025-09-29	Санкт-Петербург, Невский район, исторический район Стеклянный Городок	59.90222035	30.39402079	2025-09-29 07:04:41.13679
12	2	епнев		2025-09-29	Санкт-Петербург, Крестовый пруд	59.97100813	30.25182082	2025-09-29 07:19:16.08952
13	3	Общага	Чзнх\r\n	2025-09-29	Санкт-Петербург, Торжковская улица, 15	59.99123517	30.31918938	2025-09-29 07:34:24.715402
\.


--
-- Data for Name: photos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.photos (id, mark_id, filename, is_main, created_at) FROM stdin;
10	3	IMG_4731_1759107575.jpeg	t	2025-09-29 03:59:35.363446
11	3	IMG_4873_1759107575_0.png	f	2025-09-29 03:59:35.446154
12	3	IMG_4874_1759107575_1.png	f	2025-09-29 03:59:35.488274
13	3	IMG_4875_1759107575_2.png	f	2025-09-29 03:59:35.530928
14	4	IMG_4857_1759108011.jpeg	t	2025-09-29 04:06:51.472564
15	4	IMG_4812_1759108011_0.jpeg	f	2025-09-29 04:06:51.520385
16	4	IMG_4816_1759108011_1.jpeg	f	2025-09-29 04:06:51.572297
17	5	WIN_20240621_01_02_09_Pro_1759108312.jpg	t	2025-09-29 04:11:52.288404
18	5	WIN_20240311_13_06_13_Pro_1759108312_0.jpg	f	2025-09-29 04:11:52.333077
22	11	1000031401_1759118681_0.jpg	f	2025-09-29 07:04:41.181202
23	12	WIN_20240621_01_02_17_Pro_1759119556.jpg	t	2025-09-29 07:19:16.13649
24	13	image_1759120464.jpg	t	2025-09-29 07:34:24.721593
25	13	image_1759120464_0.jpg	f	2025-09-29 07:34:24.772252
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, telegram_id, created_at) FROM stdin;
1	855159736	2025-09-29 03:35:28.542453
2	1323961884	2025-09-29 03:56:42.269143
3	1997508478	2025-09-29 07:31:56.80601
\.


--
-- Name: marks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.marks_id_seq', 13, true);


--
-- Name: photos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.photos_id_seq', 25, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: marks marks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_pkey PRIMARY KEY (id);


--
-- Name: photos photos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_telegram_id_key UNIQUE (telegram_id);


--
-- Name: idx_marks_coordinates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_marks_coordinates ON public.marks USING btree (lat, lon);


--
-- Name: idx_marks_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_marks_user_id ON public.marks USING btree (user_id);


--
-- Name: idx_photos_is_main; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_photos_is_main ON public.photos USING btree (is_main);


--
-- Name: idx_photos_mark_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_photos_mark_id ON public.photos USING btree (mark_id);


--
-- Name: idx_users_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_telegram_id ON public.users USING btree (telegram_id);


--
-- Name: marks marks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: photos photos_mark_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_mark_id_fkey FOREIGN KEY (mark_id) REFERENCES public.marks(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

