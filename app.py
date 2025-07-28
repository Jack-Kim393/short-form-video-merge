import streamlit as st
import moviepy.editor as mp
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image
import os
import tempfile
import time
from collections import OrderedDict

# --- CONFIGURATION ---
TARGET_SIZE = (1080, 1920)
THUMBNAIL_DIR = "thumbnail"
OUTPUT_DIR = "output"
MAX_FILES = 10
OUTPUT_MAX_FILE_SIZE_MB = 32
MIN_CLIP_DURATION = 5.0
MAX_CLIP_DURATION = 15.0

# --- HELPER FUNCTIONS ---

def move_item(file_id, direction):
    """Moves an item up or down in the session state OrderedDict."""
    items = list(st.session_state.clip_settings.items())
    idx = next((i for i, (k, v) in enumerate(items) if k == file_id), None)
    
    if idx is None: return

    item = items.pop(idx)
    if direction == 'up' and idx > 0:
        items.insert(idx - 1, item)
    elif direction == 'down' and idx < len(items):
        items.insert(idx + 1, item)
    else:
        items.insert(idx, item) # Re-insert if move is not possible
    
    st.session_state.clip_settings = OrderedDict(items)

def resize_and_pad_clip(clip, target_size):
    try:
        target_w, target_h = target_size
        clip_w, clip_h = clip.size
        target_aspect = target_w / target_h
        clip_aspect = clip_w / clip_h

        if clip_aspect > target_aspect:
            new_w = target_w
            new_h = int(new_w / clip_aspect)
        else:
            new_h = target_h
            new_w = int(new_h * clip_aspect)
        
        resized_clip = clip.resize(width=new_w if clip_aspect > target_aspect else new_w, height=new_h if clip_aspect <= target_aspect else new_h)

        background = mp.ColorClip(size=target_size, color=(0, 0, 0), duration=clip.duration)
        final_clip = mp.CompositeVideoClip([background, resized_clip.set_position("center")])
        
        if clip.audio:
            final_clip.audio = clip.audio.set_duration(clip.duration)

        return final_clip.set_duration(clip.duration)
    except Exception as e:
        st.error(f"클립 리사이즈 중 오류 발생: {e}")
        return None

def create_thumbnail(video_clip, output_path):
    try:
        if not video_clip: return False
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        frame = video_clip.get_frame(0)
        img = Image.fromarray(frame)
        if img.mode == 'RGBA': img = img.convert('RGB')
        img.save(output_path, 'jpeg')
        return True
    except Exception as e:
        st.error(f"썸네일 생성 중 오류가 발생했습니다: {e}")
        return False

def get_file_id(file):
    return f"{file.name}-{file.size}-{file.file_id}"

# --- STREAMLIT UI ---
st.set_page_config(layout="wide")
st.title("🎬 간편 숏폼 영상 제작 솔루션")
st.markdown("---")

st.header("1. 영상 파일 업로드")
st.info(f"MP4 형식의 영상 파일을 1개에서 최대 {MAX_FILES}개까지 드래그앤 드랍하세요. (현재 업로드 제한: {st.config.get_option('server.maxUploadSize')}MB)")

if 'clip_settings' not in st.session_state:
    st.session_state.clip_settings = OrderedDict()

uploaded_files = st.file_uploader("파일 업로드", type=["mp4"], accept_multiple_files=True, label_visibility="collapsed")

if uploaded_files:
    if len(uploaded_files) > MAX_FILES: st.error(f"영상은 최대 {MAX_FILES}개까지 업로드할 수 있습니다."); uploaded_files = []
    
    current_files_map = {get_file_id(f): f for f in uploaded_files}
    # Add new files
    for fid, file in current_files_map.items():
        if fid not in st.session_state.clip_settings:
            with st.spinner(f"'{file.name}' 분석 중..."):
                with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as tfile:
                    tfile.write(file.getvalue())
                    try:
                        with mp.VideoFileClip(tfile.name) as clip: actual_duration = clip.duration
                    except Exception: actual_duration = MAX_CLIP_DURATION
            st.session_state.clip_settings[fid] = {'file': file, 'start': 15.0, 'duration': min(MIN_CLIP_DURATION, actual_duration), 'actual_duration': actual_duration}

    # Remove old files
    for fid in list(st.session_state.clip_settings.keys()):
        if fid not in current_files_map: del st.session_state.clip_settings[fid]

    st.markdown("---")
    st.header("2. 영상 순서 및 상세 설정")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🔄 영상 순서 및 구간 설정")
        for i, (file_id, settings) in enumerate(st.session_state.clip_settings.items()):
            with st.container(border=True):
                c1, c2 = st.columns([0.85, 0.15])
                with c1:
                    thumbnail_indicator = "👑 (썸네일)" if i == 0 else ""
                    with st.expander(f"**{i+1}. {settings['file'].name}** ({settings['actual_duration']:.2f}초) {thumbnail_indicator}", expanded=True):
                        sc1, sc2 = st.columns(2)
                        actual_dur = settings['actual_duration']
                        settings['start'] = sc1.number_input("시작 시간 (초)", 0.0, max(0.0, actual_dur - MIN_CLIP_DURATION), settings['start'], 0.1, "%.1f", key=f"start_{file_id}")
                        settings['duration'] = sc2.number_input("사용할 길이 (초)", MIN_CLIP_DURATION, min(MAX_CLIP_DURATION, actual_dur), settings['duration'], 0.1, "%.1f", key=f"duration_{file_id}")
                with c2:
                    if i > 0: st.button("🔼", key=f"up_{file_id}", on_click=move_item, args=(file_id, 'up'), use_container_width=True)
                    if i < len(st.session_state.clip_settings) - 1: st.button("🔽", key=f"down_{file_id}", on_click=move_item, args=(file_id, 'down'), use_container_width=True)

    with col2:
        st.subheader("✨ 전환 효과 설정")
        transition_sec = st.slider("전환 시간 (초)", 0.1, 1.0, 0.5, 0.05, help="영상 간 전환 효과 길이 (0.1초 ~ 1.0초)")

    # --- 3. 영상 생성 ---
    st.markdown("---")
    st.header("3. 최종 영상 생성")
    if st.button("🚀 영상 생성 시작!", type="primary", use_container_width=True):
        source_clips, processed_clips, temp_files = [], [], []
        final_video = None
        try:
            with st.spinner("영상을 처리 중입니다. 잠시만 기다려주세요..."):
                for i, clip_info in enumerate(st.session_state.clip_settings.values()):
                    st.write(f"({i+1}/{len(st.session_state.clip_settings)}) '{clip_info['file'].name}' 처리 중...")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
                        tfile.write(clip_info['file'].getvalue())
                        temp_files.append(tfile.name)
                    
                    clip = mp.VideoFileClip(tfile.name)
                    source_clips.append(clip)

                    if clip_info['start'] + clip_info['duration'] > clip.duration + 0.1:
                        st.error(f"'{clip_info['file'].name}'의 설정된 구간이 영상 총 길이를 초과합니다."); st.stop()

                    subclip = clip.subclip(clip_info['start'], clip_info['start'] + clip_info['duration'])
                    resized_clip = resize_and_pad_clip(subclip, TARGET_SIZE)
                    if not resized_clip: st.error(f"'{clip_info['file'].name}' 처리 실패."); st.stop()
                    processed_clips.append(resized_clip)

                safety_margin = 0.85
                total_duration = sum(c.duration for c in processed_clips)
                target_bitrate_kbps = ((OUTPUT_MAX_FILE_SIZE_MB * safety_margin * 1024 * 8) / total_duration)
                video_bitrate_kbps = target_bitrate_kbps - 128
                if video_bitrate_kbps < 500: st.warning("⚠️ 영상 길이가 길어 화질이 낮을 수 있습니다.")

                thumb_path = os.path.join(THUMBNAIL_DIR, f"thumbnail_{int(time.time())}.jpg")
                if not create_thumbnail(processed_clips[0], thumb_path): st.error("썸네일 생성 실패."); st.stop()

                clips_with_fade = [processed_clips[0]] + [clip.fx(fadein, transition_sec) for clip in processed_clips[1:]]
                final_video = mp.concatenate_videoclips(clips_with_fade, method="compose").fx(fadein, transition_sec).fx(fadeout, transition_sec)

                output_dir_abs = os.path.abspath(OUTPUT_DIR)
                os.makedirs(output_dir_abs, exist_ok=True)
                output_path = os.path.join(output_dir_abs, f"shortform_{int(time.time())}.mp4")
                final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate=f"{int(video_bitrate_kbps)}k", threads=4, logger='bar')

                final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                if final_size_mb > OUTPUT_MAX_FILE_SIZE_MB:
                    st.error(f"최종 영상 크기({final_size_mb:.2f}MB)가 목표({OUTPUT_MAX_FILE_SIZE_MB}MB)를 초과했습니다.")
                else:
                    st.success(f"🎉 영상 생성 완료! (크기: {final_size_mb:.2f}MB)")
                    st.balloons()
                    
                    # --- 4. 결과물 다운로드 제공 ---
                    st.markdown("---")
                    st.header("4. 결과물 다운로드")
                    
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.video(output_path)
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="✅ 최종 영상 다운로드 (.mp4)",
                                data=file,
                                file_name=os.path.basename(output_path),
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    with dl_col2:
                        st.image(thumb_path, caption="생성된 썸네일")
                        with open(thumb_path, "rb") as file:
                            st.download_button(
                                label="🖼️ 썸네일 다운로드 (.jpg)",
                                data=file,
                                file_name=os.path.basename(thumb_path),
                                mime="image/jpeg",
                                use_container_width=True
                            )

        except Exception as e:
            st.error(f"영상 생성 중 심각한 오류가 발생했습니다: {e}")
        finally:
            if final_video: final_video.close()
            for clip in processed_clips: 
                if clip: clip.close()
            for clip in source_clips:
                if clip: clip.close()
            for path in temp_files:
                if os.path.exists(path): os.unlink(path)